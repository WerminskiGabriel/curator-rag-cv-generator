"""
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
"""
from langchain_huggingface import HuggingFaceEmbeddings

_embeddings = None

def get_embedding_function():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _embeddings
