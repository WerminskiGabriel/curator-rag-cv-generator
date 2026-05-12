from django.contrib import admin
from . import models
from .models import JobOffer


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'scraped_at')
    search_fields = ('slug', 'title')
    list_filter = ('scraped_at',)
    readonly_fields = ('scraped_at',)

admin.site.register(models.Profile)
admin.site.register(models.Documents)
