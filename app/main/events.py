from flask import session, current_app
from flask_socketio import emit, join_room
from app import socketio
from app.modules.session_store import store
from app.modules.rag_engine import RAGManager
from app.modules.analysis_engine import analyze_csv
from app.modules.llm_engine import get_llm
import os


@socketio.on('connect')
def handle_connect():
    sid = session.get('session_id', 'unknown')
    join_room(sid)
    emit('connected', {'status': 'Connected to Founders Vault', 'session_id': sid})


@socketio.on('process_file')
def handle_process(data):
    """Process file after upload (for PDFs mainly)"""
    sid = session.get('session_id')
    file_info = store.get(sid, 'current_file')
    model = store.get(sid, 'selected_model')
    clean_db = store.get(sid, 'clean_db_flag', False)

    if not file_info:
        emit('error', {'message': 'No file found'})
        return

    try:
        if file_info['type'] == 'pdf':
            # 1. Reading Stage
            emit('status', {'message': 'Reading PDF Document...', 'icon': '📄'})
            socketio.sleep(0.5)

            # 2. Vectorization Stage
            emit('status', {'message': 'Generating Vector Embeddings...', 'icon': '🧠'})

            rag_manager = RAGManager(current_app.config['CHROMA_DB_PATH'])
            vectordb, llm = rag_manager.process_pdf(
                file_info['path'],
                file_info['name'],
                model,
                clean_db=clean_db
            )

            store.set(sid, 'vectordb', vectordb)
            store.set(sid, 'llm', llm)
            store.set(sid, 'mode', 'pdf')

            # 3. Finalization Stage
            emit('status', {'message': 'Finalizing Knowledge Base...', 'icon': '💾'})
            socketio.sleep(0.5)

            emit('ready', {'mode': 'pdf', 'message': 'PDF processed successfully'})

        elif file_info['type'] == 'csv':
            emit('status', {'message': 'Loading CSV Data...', 'icon': '📊'})
            socketio.sleep(0.5)

            agent, df = analyze_csv(file_info['path'], model)

            store.set(sid, 'csv_agent', agent)
            store.set(sid, 'csv_path', file_info['path'])
            store.set(sid, 'mode', 'csv')
            store.set(sid, 'df_preview', df.head(10).to_html(classes='table table-dark table-sm table-striped'))

            emit('ready', {
                'mode': 'csv',
                'preview': store.get(sid, 'df_preview'),
                'message': 'CSV ready for analysis'
            })

    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('chat_message')
def handle_message(data):
    """Handle chat queries with Thinking -> Indexing -> Answer flow"""
    sid = session.get('session_id')
    query = data.get('message', '')
    mode = store.get(sid, 'mode')

    if not query:
        return

    # Add user message to history
    messages = store.get(sid, 'messages', [])
    messages.append({'role': 'user', 'content': query})

    try:
        if mode == 'pdf':
            vectordb = store.get(sid, 'vectordb')
            llm = store.get(sid, 'llm')

            if not vectordb:
                emit('error', {'message': 'PDF not processed yet'})
                return

            # STEP 1: THINKING
            emit('process_status', {'step': 'thinking', 'message': '🤔 Deconstructing query...'})
            socketio.sleep(0.5)

            rag_manager = RAGManager(current_app.config['CHROMA_DB_PATH'])

            # Retrieve documents for indexing display
            retriever = vectordb.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(query)

            # STEP 2: SHOW INDEXING CARDS
            snippets = []
            for i, doc in enumerate(docs):
                snippets.append({
                    'id': i + 1,
                    'page': doc.metadata.get('page', '?'),
                    'content': doc.page_content[:150] + "..."
                })

            emit('process_status', {
                'step': 'indexing',
                'message': f'🔍 Indexed {len(docs)} relevant segments',
                'data': snippets
            })
            # Brief pause to let user see the cards before streaming starts
            socketio.sleep(1.0)

            # STEP 3: STREAMING ANSWER (Removed "Summarising" bubble)
            stream_gen, _ = rag_manager.query(vectordb, llm, query)

            full_response = ""
            emit('stream_start', {})

            for chunk in stream_gen:
                text_chunk = chunk if isinstance(chunk, str) else chunk.get('text', '')
                full_response += text_chunk
                emit('stream_chunk', {'chunk': text_chunk})

            emit('stream_end', {'sources': ''})

            messages.append({'role': 'assistant', 'content': full_response})

        elif mode == 'csv':
            # CSV Analysis Mode
            emit('process_status', {'step': 'thinking', 'message': '🔍 Analyzing tabular data...'})

            file_path = store.get(sid, 'csv_path')
            model = store.get(sid, 'selected_model')
            agent, _ = analyze_csv(file_path, model)

            response = agent.run(query)

            emit('response', {
                'role': 'assistant',
                'content': response,
                'mode': 'csv'
            })

            messages.append({
                'role': 'assistant',
                'content': response
            })

        store.set(sid, 'messages', messages)

    except Exception as e:
        emit('error', {'message': f'Error: {str(e)}'})