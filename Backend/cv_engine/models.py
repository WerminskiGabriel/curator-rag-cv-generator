from django.db import models
from ..api.models import Documents
from pgvector import VectorField


class CVAnalysis(models.Model):
    document = models.ForeignKey( Documents, on_delete=models.CASCADE)
    raw_text_chunk = models.TextField()
    embedding = VectorField(dimensions=384)

    def __str__(self):
        return f"{self.document.id}|{self.raw_text_chunk[:30]}"
