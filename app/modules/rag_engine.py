import os
import shutil
import gc
import time
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from app.modules.llm_engine import get_llm, get_embeddings


class RAGManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.embeddings = get_embeddings()

    def process_documents(self, file_infos, model_name, clean_db=False):
        """Process multiple PDFs into a unified vector store"""
        llm = get_llm(model_name)

        if clean_db and os.path.exists(self.db_path):
            try:
                gc.collect()  # Release file locks for Windows
                time.sleep(0.1)
                shutil.rmtree(self.db_path)
            except OSError as e:
                print(f"⚠️ Warning: Could not wipe DB: {e}")

        all_docs = []
        for file_info in file_infos:
            loader = PyMuPDFLoader(file_info['path'])
            docs = loader.load()
            for doc in docs:
                doc.metadata['source_file'] = file_info['name']
            all_docs.extend(docs)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
        splits = text_splitter.split_documents(all_docs)

        vectordb = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.db_path
        )
        return vectordb, llm

    def query(self, vectordb, llm, query, k=5, answer_length="short"):
        """
        Execute query with dynamic chunk retrieval (k) and prompt instructions (answer_length).
        """
        retriever = vectordb.as_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(query)

        context_text = ""
        for d in docs:
            context_text += f"[Source: {d.metadata.get('source_file')}]\n{d.page_content}\n\n"

        # --- DYNAMIC PROMPT INSTRUCTION ---
        if answer_length == 'short':
            # Forces the model to be concise for "2 mark" style answers
            system_instruction = "You are a concise assistant. Answer the question in small 5 point by point or a 9 line paragraph."
        else:
            system_instruction = "You are a helpful assistant. Provide a comprehensive and detailed answer. Structure your answer with clear paragraphs and bold text headings."

        prompt = f"""{system_instruction}

        Answer based ONLY on the context provided below.

        <context>
        {context_text}
        </context>

        Question: {query}"""

        return llm.stream(prompt), docs