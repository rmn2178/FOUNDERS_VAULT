from langchain_ollama import OllamaLLM
from langchain_community.embeddings import FastEmbedEmbeddings
from functools import lru_cache

@lru_cache(maxsize=None)
def get_llm(model_name="llama3.2:latest", temperature=1):
    """Cached LLM initialization using modern OllamaLLM"""
    return OllamaLLM(
        model=model_name,
        temperature=temperature,
        keep_alive="1h"
    )

@lru_cache(maxsize=None)
def get_embeddings():
    """Cached High-Speed Embeddings using FastEmbed (ONNX Optimized)"""
    print("⚡ Loading FastEmbed (CPU Optimized)...")
    return FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")