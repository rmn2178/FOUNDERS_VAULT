from flask import session, current_app
from flask_socketio import emit, join_room
from app import socketio
from app.modules.session_store import store
from app.modules.rag_engine import RAGManager
from app.modules.analysis_engine import analyze_csvs
from app.modules.llm_engine import get_llm
import os
import time


@socketio.on('connect')
def handle_connect():
    sid = session.get('session_id', 'unknown')
    join_room(sid)
    emit('connected', {'status': 'Connected to Founders Vault', 'session_id': sid})


@socketio.on('process_file')
def handle_process(data):
    sid = session.get('session_id')
    files = store.get(sid, 'uploaded_files')
    model = store.get(sid, 'selected_model')
    clean_db = store.get(sid, 'clean_db_flag', False)

    if not files:
        emit('error', {'message': 'No documents found'})
        return

    try:
        main_type = files[0]['type']

        if main_type == 'pdf':
            emit('status', {'message': f'Reading {len(files)} PDFs...', 'icon': '📄'})
            rag_manager = RAGManager(current_app.config['CHROMA_DB_PATH'])
            vectordb, llm = rag_manager.process_documents(files, model, clean_db=clean_db)

            store.set(sid, 'vectordb', vectordb)
            store.set(sid, 'llm', llm)
            store.set(sid, 'mode', 'pdf')
            emit('ready', {'mode': 'pdf', 'message': 'PDFs processed'})

        elif main_type == 'csv':
            emit('status', {'message': f'Analyzing {len(files)} CSVs...', 'icon': '📊'})
            agent, dfs = analyze_csvs(files, model)

            store.set(sid, 'csv_agent', agent)
            store.set(sid, 'mode', 'csv')

            preview_html = dfs[0].head(5).to_html(classes='table table-dark table-sm table-striped')
            emit('ready', {'mode': 'csv', 'preview': preview_html, 'message': 'CSVs ready'})

    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('chat_message')
def handle_message(data):
    sid = session.get('session_id')
    query = data.get('message', '')
    mode = store.get(sid, 'mode')

    # Retrieve User Preference for Answer Length
    length_pref = store.get(sid, 'answer_length', 'short')
    k_chunks = 3 if length_pref == 'short' else 10

    if not query: return

    try:
        if mode == 'pdf':
            vectordb = store.get(sid, 'vectordb')
            llm = store.get(sid, 'llm')

            emit('process_status', {'step': 'thinking', 'message': '🤔 Searching Vault...'})

            # Indexing logic - Use dynamic k_chunks
            retriever = vectordb.as_retriever(search_kwargs={"k": k_chunks})
            docs = retriever.invoke(query)

            snippets = [{'id': i + 1, 'page': d.metadata.get('source_file'), 'content': d.page_content[:100]} for i, d
                        in enumerate(docs)]

            msg = f"🔍 Found {len(docs)} sources ({length_pref} mode)"
            emit('process_status', {'step': 'indexing', 'message': msg, 'data': snippets})
            time.sleep(0.5)

            rag_manager = RAGManager(current_app.config['CHROMA_DB_PATH'])

            # Pass dynamic k_chunks to the query engine
            stream_gen, _ = rag_manager.query(vectordb, llm, query, k=k_chunks)

            emit('stream_start', {})
            for chunk in stream_gen:
                emit('stream_chunk', {'chunk': chunk})
            emit('stream_end', {})

        elif mode == 'csv':
            emit('process_status', {'step': 'thinking', 'message': '📊 Computing...'})
            agent = store.get(sid, 'csv_agent')
            response = agent.run(query)
            emit('response', {'role': 'assistant', 'content': response})

    except Exception as e:
        emit('error', {'message': f'Error: {str(e)}'})