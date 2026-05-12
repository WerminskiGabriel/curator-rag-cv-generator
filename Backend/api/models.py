from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Profile:{self.user}"

class Documents(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    uploadDate = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="import/",null=True,blank=True)
    text = models.TextField(null=True, blank=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.profile} | {self.uploadDate}"

class JobOffer(models.Model):
    slug = models.CharField(max_length=255, unique=True, primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, default='')
    required_skills = models.JSONField(default=list)
    scraped_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_offers'

    def __str__(self):
        return f"{self.title} ({self.slug})"
