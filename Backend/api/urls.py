from django.urls import path
from .views import offer_views, resume_views, document_views, authorization
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', authorization.register, name='register'),
    path('profile/', authorization.UserProfileView.as_view(), name='user_profile'),

    path('offers/get-offers/', offer_views.get_offers_from_db),
    path('offers/scrape/', offer_views.scrape_offers),

    path('resume/generate-cv/', resume_views.auto_generate_cv),

    path('documents/import-file/', document_views.import_file),
    path('documents/import-txt/', document_views.import_txt),
    path('documents/get-documents/', document_views.get_profile_document_objects),
    path('documents/<int:documents_id>/delete-document/', document_views.delete_document),
    path('documents/<int:documents_id>/get_document_status/', document_views.get_document_status),
    path('documents/<int:documents_id>/get_document/', document_views.get_document_objects),

]
