import os
import uuid
from flask import render_template, request, redirect, url_for, flash, session, current_app
from app.main import bp
from app.modules.session_store import store
from app.modules.system_check import check_ollama_status
from werkzeug.utils import secure_filename


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'csv'}


@bp.before_request
def make_session_id():
    """Ensure each browser session has a unique ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())


@bp.route('/')
def index():
    if not check_ollama_status():
        flash("🚨 Ollama is not running! Please run 'ollama serve' in your terminal.", "error")

    models = current_app.config['MODEL_OPTIONS']
    current_file = store.get(session['session_id'], 'current_file')
    return render_template('index.html', models=models, current_file=current_file)


@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('main.index'))

    file = request.files['file']
    model = request.form.get('model', 'llama3.2:latest')

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('main.index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Check if we already have a file and need to handle merge/clean
        existing_file = store.get(session['session_id'], 'current_file')
        action = request.form.get('action', 'replace')  # 'replace' or 'merge'

        if existing_file and existing_file['name'] != filename:
            if action == 'replace':
                store.set(session['session_id'], 'clean_db_flag', True)
            else:
                store.set(session['session_id'], 'clean_db_flag', False)

        file.save(file_path)

        # Store file info
        store.set(session['session_id'], 'current_file', {
            'name': filename,
            'path': file_path,
            'type': filename.rsplit('.', 1)[1].lower()
        })
        store.set(session['session_id'], 'selected_model', model)
        store.set(session['session_id'], 'messages', [])

        return redirect(url_for('main.chat'))

    flash('Invalid file type. Only PDF and CSV allowed.', 'error')
    return redirect(url_for('main.index'))


@bp.route('/chat')
def chat():
    current_file = store.get(session['session_id'], 'current_file')
    if not current_file:
        flash('Please upload a document first', 'warning')
        return redirect(url_for('main.index'))

    model = store.get(session['session_id'], 'selected_model', 'llama3.2:latest')
    messages = store.get(session['session_id'], 'messages', [])
    models = current_app.config['MODEL_OPTIONS']

    return render_template('chat.html',
                           current_file=current_file,
                           selected_model=model,
                           models=models,
                           messages=messages)


@bp.route('/clear', methods=['POST'])
def clear_session():
    """Clear chat history but keep the file"""
    store.set(session['session_id'], 'messages', [])
    flash('Chat history cleared', 'success')
    return redirect(url_for('main.chat'))


@bp.route('/new-session')
def new_session():
    """Start completely fresh"""
    store.clear(session['session_id'])
    session.clear()
    flash('New session started', 'success')
    return redirect(url_for('main.index'))