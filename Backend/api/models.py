from django.db import models
from django.contrib.auth.models import User
import uuid


class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remote = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    documentId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Profile: {self.user}"


class Documents(models.Model):
    documentId = models.ForeignKey(Profile, on_delete=models.CASCADE)
    uploadDate = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="import/")
    text = models.TextField(null=True)
