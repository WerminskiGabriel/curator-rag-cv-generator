from django.urls import path
from cv_engine.views import fill_cv, create_resume_pdf
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('fill-cv/<int:profile_id>/', fill_cv.generate_and_fill_cv_to_model, name='fill_cv'),
    path('create-resume-pdf/<int:generatedResume_id>/', create_resume_pdf.generate_cv, name="create_resume_pdf"),
]
