from django.db import models
from django.utils.text import slugify
from accounts.models import User
from utils.models import TimeStampedModel
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

# Create your models here.

class Community(TimeStampedModel):
    hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='administered_communities')
    members = models.ManyToManyField(User, related_name='communities', blank=True)
    slug = models.SlugField(max_length=100, blank=True)
    search_vector = models.SearchVectorField(null=True)
    description = models.TextField(null=True)
    meta_keywords = models.CharField('Meta Keywords', null=True, max_length=255, help_text='Comma delimited set of SEO keywords for meta tag')
    meta_description = models.CharField('Meta Description', null=True, max_length=255, help_text='Content for description meta tag')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('hub', 'slug')  # Ensures slug is unique per hub
        ordering = ['-created_at']
        indexes = [
            GinIndex(fields=['search_vector'], name='post_search_idx'),
        ]

    def __str__(self):
        return f"{self.name} (Hub: {self.hub.name})"