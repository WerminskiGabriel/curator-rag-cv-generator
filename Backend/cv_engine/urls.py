from django.urls import path
from cv_engine.views import fill_cv, create_resume_pdf

urlpatterns = [
    path('fill-cv/<int:profile_id>/', fill_cv.generate_and_fill_cv_to_model, name='fill_cv'),
    path('generation-status/<str:task_id>/', fill_cv.generation_status, name='generation_status'),
    path('create-resume-pdf/<int:generatedResume_id>/', create_resume_pdf.generate_cv, name='create_resume_pdf'),
]
