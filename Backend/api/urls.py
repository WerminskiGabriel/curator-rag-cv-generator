from django.urls import path
from .views import offer_views, resume_views, supabase_views, document_views


urlpatterns = [
    path('offers/match/', offer_views.match),
    path('offers/scan-save/', offer_views.scan_and_save_offers),

    path('supabase/select/', supabase_views.supabase_select),
    path('supabase/insert/', supabase_views.supabase_insert),
    path('supabase/update/', supabase_views.supabase_update),
    path('supabase/delete/', supabase_views.supabase_delete),


    path('resume/generate-cv/', resume_views.auto_generate_cv),

    path('documents/import_file', document_views.import_file),
    path('documents/import_txt', document_views.import_txt),
    path('documents/delete_document', document_views.delete_document),
    path('documents/get_document_status', document_views.get_document_status),
    path('documents/get_document', document_views.get_document_objects),
    path('documents/get_ducuments', document_views.get_profile_document_objects),


]
