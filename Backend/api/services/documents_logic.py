from .. import models
from .parser import parser_path
from ..models import Documents


# ----------[ GETTERS ]----------
def get_documents_object(documents_id):
    try:
        return models.Documents.objects.get(id=documents_id)
    except Documents.DoesNotExist as e:
        print(e)
        return None


def get_documents_profile(documents_id):
    documents_obj = get_documents_object(documents_id)
    return documents_obj.profile


def get_documents_uploadDate(documents_id):
    documents_obj = get_documents_object(documents_id)
    return documents_obj.uploadDate


def get_documents_file(documents_id):
    documents_obj = get_documents_object(documents_id)
    return documents_obj.file


def get_documents_text(documents_id):
    documents_obj = get_documents_object(documents_id)
    return documents_obj.text


# --------------------
def txt_upload_to_model(documents_id):
    txt = txt_extract(documents_id)
    if txt:
        models.Documents.objects.filter(id=documents_id).update(text=txt, processed=True)


# --------------------
def txt_extract(documents_id):
    file = get_documents_file(documents_id)

    file_path = file.path
    txt_from_file = parser_path(file_path)
    return txt_from_file


def document_to_dict(doc):
    try:
        return {
            "id": doc.id,
            "processed": doc.processed,
            "uploadDate": doc.uploadDate,
            "text": doc.text,
            "filePath": doc.file.url if doc.file else None,
        }
    except ValueError:
        return {"error": "Document does not exist"}
