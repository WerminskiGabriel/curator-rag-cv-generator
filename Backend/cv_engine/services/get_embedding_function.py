"""
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
"""
from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_function():
    #embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    #embeddings = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    #embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
