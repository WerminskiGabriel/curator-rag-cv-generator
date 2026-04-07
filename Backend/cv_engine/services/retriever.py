#from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
#from langchain_core.retrievers import BaseRetriever
from pgvector.django import CosineDistance
#from langchain_openai import OpenAIEmbeddings
#from django.conf import settings
from ..models import CVAnalysis
from .get_embedding_function import get_embedding_function

def retriever(query,document_id, max_results=5):
    embeddings_function = get_embedding_function()
    query_embedding = embeddings_function.embed_query(query)
    retrieved_chunks = CVAnalysis.objects.filter(document_id=document_id).annotate(
        distance=CosineDistance("embedding", query_embedding)
    ).order_by("distance")

    return [Document(page_content=chunk.raw_text_chunk) for chunk in retrieved_chunks[:max_results]]
