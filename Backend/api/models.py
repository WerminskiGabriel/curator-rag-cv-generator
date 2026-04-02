from django.db import models
from django.contrib.auth.models import User
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save


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

    def __str__(self):
        return f"Profile:{self.user}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Documents(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    uploadDate = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="import/",null=True,blank=True)
    text = models.TextField(null=True, blank=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.profile} | {self.uploadDate}"
