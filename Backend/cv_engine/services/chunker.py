from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document


def spacy_chunker(text):
    pass


def chunker(document, chunk_size=400, chunk_overlap=200):
    """
    Performs fixed-size chunking on a document with specified overlap.

    Args:
        document (str): The text document to process
        chunk_size (int): The target size of each chunk in characters
        chunk_overlap (int): The number of characters of overlap between chunks

    Returns:
        list: The chunked documents with metadata
    """

    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    chunks = text_splitter.split_text(document)
    print(f"Document split into {len(chunks)} chunks")

    documents_to_save = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "chunk_id": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk),
                "chunk_type": "fixed-size"
            }
        )
        documents_to_save.append(doc)

    return documents_to_save
