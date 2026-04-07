from django.contrib import admin
from .models import Offer

from . import models

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'salary', 'remote', 'created_at')
    list_filter = ('remote', 'created_at')
    search_fields = ('title', 'description')


admin.site.register(models.Profile)
admin.site.register(models.Documents)
