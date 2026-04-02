from .. import models
from parser import parser_path


# ----------[ GETTERS ]----------
def get_documents_object(documents_id):
    document_record = models.Documents.objects.filter(id=documents_id).first()

    if not document_record:
        return None
    return document_record


def get_documents_profile(documents_id):
    documents_obj = get_documents_object(documents_id)
    return documents_obj.profile if documents_obj else None


def get_documents_uploadDate(documents_id):
    documents_obj = get_documents_object(documents_id)
    return documents_obj.uploadDate if documents_obj else None


def get_documents_file(documents_id):
    documents_obj = get_documents_object(documents_id)
    return documents_obj.file if documents_obj else None


def get_documents_text(documents_id):
    documents_obj = get_documents_object(documents_id)
    return documents_obj.text if documents_obj else None


# --------------------
def txt_upload_to_model(documents_id):
    txt = txt_extract(documents_id)
    if txt:
        models.Documents.objects.filter(id=documents_id).update(text=txt, processed=True)


# --------------------
def txt_extract(documents_id):
    file = get_documents_file(documents_id)

    if file:
        file_path = file.path()
        txt_from_file = parser_path(file_path)
        return txt_from_file
    return None
