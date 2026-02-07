import os
import uuid
from flask import render_template, request, redirect, url_for, flash, session, current_app
from app.main import bp
from app.modules.session_store import store
from app.modules.system_check import check_ollama_status, get_ollama_models
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """Check if the file extension is supported"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'csv'}


@bp.before_request
def make_session_id():
    """Ensure each browser session has a unique ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())


@bp.route('/')
def index():
    """Landing page with dynamic model selection and upload area"""
    if not check_ollama_status():
        flash("🚨 Ollama is not running! Please run 'ollama serve' in your terminal.", "error")

    # Fetch models dynamically from the device
    models = get_ollama_models()

    files = store.get(session['session_id'], 'uploaded_files')
    return render_template('index.html', models=models, uploaded_files=files)


@bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle multiple file uploads and clean up previous session data"""
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('main.index'))

    # Retrieve inputs
    files = request.files.getlist('file')
    model = request.form.get('model', 'llama3.2:latest')
    answer_length = request.form.get('answer_length', 'short')  # 'short' or 'long'

    if not files or files[0].filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('main.index'))

    # --- DELETE PREVIOUS FILES & PREPARE CLEAN SLATE ---
    previous_files = store.get(session['session_id'], 'uploaded_files', [])
    if previous_files:
        for old_file in previous_files:
            try:
                if os.path.exists(old_file['path']):
                    os.remove(old_file['path'])
                    print(f"🗑️ Deleted previous file: {old_file['name']}")
            except Exception as e:
                print(f"⚠️ Error deleting previous file: {e}")

    # Flag to wipe Vector DB (handled in events.py -> rag_engine.py)
    store.set(session['session_id'], 'clean_db_flag', True)
    # ---------------------------------------------------

    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            saved_files.append({
                'name': filename,
                'path': file_path,
                'type': filename.rsplit('.', 1)[1].lower()
            })

    if not saved_files:
        flash('Invalid file type. Only PDF and CSV allowed.', 'error')
        return redirect(url_for('main.index'))

    # Store settings in session
    store.set(session['session_id'], 'uploaded_files', saved_files)
    store.set(session['session_id'], 'selected_model', model)
    store.set(session['session_id'], 'answer_length', answer_length)
    store.set(session['session_id'], 'messages', [])

    return redirect(url_for('main.chat'))


@bp.route('/chat')
def chat():
    """Chat interface with the list of processed documents"""
    files = store.get(session['session_id'], 'uploaded_files')
    if not files:
        flash('Please upload documents first', 'warning')
        return redirect(url_for('main.index'))

    model = store.get(session['session_id'], 'selected_model', 'llama3.2:latest')
    messages = store.get(session['session_id'], 'messages', [])

    # --- FIX APPLIED HERE ---
    # Fetch models dynamically so the template can find 'model.mode' for the sidebar badge
    models = get_ollama_models()

    # Safeguard: If the selected model isn't in the list (e.g. API temporary glitch),
    # add a fallback to prevent 'dict object has no attribute' error.
    if model not in models:
        models[model] = {'name': model, 'mode': 'speed'}
    # ------------------------

    return render_template('chat.html',
                           uploaded_files=files,
                           selected_model=model,
                           models=models,
                           messages=messages)


@bp.route('/clear', methods=['POST'])
def clear_session():
    """Clear chat history but keep the uploaded files"""
    store.set(session['session_id'], 'messages', [])
    flash('Chat history cleared', 'success')
    return redirect(url_for('main.chat'))


@bp.route('/new-session')
def new_session():
    """Start completely fresh: clear files, DB, and history"""
    store.clear(session['session_id'])
    session.clear()
    flash('New session started', 'success')
    return redirect(url_for('main.index'))