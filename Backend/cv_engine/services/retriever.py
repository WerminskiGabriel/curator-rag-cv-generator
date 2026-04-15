from langchain_core.documents import Document
from pgvector.django import CosineDistance
from cv_engine.models import CVAnalysis
from cv_engine.services.get_embedding_function import get_embedding_function


def retriever(query, profile_id, max_results=5):
    embeddings_function = get_embedding_function()
    query_embedding = embeddings_function.embed_query(query)
    retrieved_chunks = CVAnalysis.objects.filter(document__profile_id=profile_id).annotate(
        distance=CosineDistance("embedding", query_embedding)
    ).order_by("distance")

    return [Document(page_content=chunk.raw_text_chunk) for chunk in retrieved_chunks[:max_results]]
