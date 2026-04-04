from django.dispatch import receiver
from django.db.models.signals import post_save
from .. import models
from django.contrib.auth.models import User

from ..services.documents_logic import txt_upload_to_model


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        models.Profile.objects.create(user=instance)


@receiver(post_save, sender=models.Documents)
def parse_file(sender, instance, created, **kwargs):
    if not instance.processed and bool(instance.file):
        txt_upload_to_model(instance.id)
