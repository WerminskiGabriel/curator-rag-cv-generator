import uuid

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


class GenerationTask(models.Model):
    STATUS_RUNNING = 'running'
    STATUS_DONE = 'done'
    STATUS_ERROR = 'error'

    task_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default=STATUS_RUNNING)
    progress = models.IntegerField(default=0)
    current = models.CharField(max_length=200, default='Starting…')
    done_sections = models.IntegerField(default=0)
    total_sections = models.IntegerField(default=5)
    generated_resume = models.ForeignKey(
        GeneratedResume, null=True, blank=True, on_delete=models.SET_NULL
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
