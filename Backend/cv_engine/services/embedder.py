from cv_engine.models import CVAnalysis
from cv_engine.services.chunker import chunker
from cv_engine.services.get_embedding_function import get_embedding_function


def process_document_to_db(document_instance):
    raw_text = document_instance.text
    if not raw_text:
        return

    chunks = chunker(raw_text)

    embedding_fuction = get_embedding_function()

    for chunk in chunks:
        vector = embedding_fuction.embed_query(chunk.page_content)

        CVAnalysis.objects.create(
            document=document_instance,
            raw_text_chunk=chunk.page_content,
            embedding=vector,
        )
