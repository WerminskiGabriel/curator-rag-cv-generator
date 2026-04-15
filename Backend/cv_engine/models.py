from django.db import models
from django.contrib.auth.models import User
from api.models import Documents
from pgvector.django import VectorField


class CVAnalysis(models.Model):
    document = models.ForeignKey(Documents, on_delete=models.CASCADE)
    raw_text_chunk = models.TextField()
    embedding = VectorField(dimensions=384)

    def __str__(self):
        return f"{self.document.id}|{self.raw_text_chunk[:30]}"


class GeneratedResume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # job_id = models. TODO
    generatedJson = models.JSONField()
    pdf_file = models.FileField(upload_to='resumes/', null=True, blank=True)
