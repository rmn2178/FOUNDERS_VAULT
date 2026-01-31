import os
import shutil
import gc
import time
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from app.modules.llm_engine import get_llm, get_embeddings


class RAGManager:
    """Pure RAG implementation without Streamlit dependencies"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.embeddings = get_embeddings()

    def process_pdf(self, file_path, file_name, model_name, clean_db=False):
        """Process PDF and return vectordb and llm instances"""
        llm = get_llm(model_name)

        # --- ROBUST DB DELETION LOGIC ---
        if clean_db and os.path.exists(self.db_path):
            try:
                gc.collect()
                time.sleep(0.1)
                shutil.rmtree(self.db_path)
                print("🗑️ Previous Vector DB wiped successfully.")
            except OSError as e:
                print(f"⚠️ Warning: Could not fully wipe DB: {e}")
        # -------------------------------------

        # Load and split PDF
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        # Create vector store
        vectordb = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.db_path
        )

        return vectordb, llm

    def get_existing_db(self):
        if os.path.exists(self.db_path) and os.listdir(self.db_path):
            return Chroma(
                persist_directory=self.db_path,
                embedding_function=self.embeddings
            )
        return None

    def query(self, vectordb, llm, query):
        """Execute RAG query with streaming support"""
        # Fetch relevant docs
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(query)

        context_text = "\n\n".join([d.page_content for d in docs])

        # --- IMPROVED STRUCTURAL PROMPT ---
        prompt = f"""You are a helpful and organized assistant. Answer the question based ONLY on the provided context.

        FORMATTING INSTRUCTIONS:
        - Use clear paragraphs for explanations.
        - Use bullet points or numbered lists if listing multiple items.
        - Use bold text for key terms.
        - Do NOT dump text in a single block. Structure your answer.

        <context>
        {context_text}
        </context>

        Question: {query}
        """

        # Return generator for streaming
        stream_generator = llm.stream(prompt)
        return stream_generator, docs