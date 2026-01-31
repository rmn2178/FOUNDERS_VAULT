from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from functools import lru_cache

@lru_cache(maxsize=None)
def get_llm(model_name="llama3.2:latest", temperature=0):
    """Cached LLM initialization (replaces @st.cache_resource)"""
    return Ollama(
        model=model_name,
        temperature=temperature,
        keep_alive="1h"
    )

@lru_cache(maxsize=None)
def get_embeddings():
    """Cached Embeddings (replaces @st.cache_resource)"""
    print("⚡ Loading High-Speed Local Embeddings...")
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")