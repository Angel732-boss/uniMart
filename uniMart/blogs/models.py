from django.db import models
from django.utils.text import slugify
from accounts.models import User
from utils.models import TimeStampedModel
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

# Create your models here.

class Post(TimeStampedModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    hub = models.ForeignKey('hubs.Hub', on_delete=models.PROTECT, related_name='posts')
    category = models.ForeignKey('utils.Category', limit_choices_to={'service_type'}, on_delete=models.PROTECT, related_name='posts')
    tags = models.ManyToManyField('utils.Tag', blank=True)
    slug = models.SlugField(blank=True)
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        unique_together = [['hub', 'slug']]
        ordering = ['-created_at']
        indexes = [
            GinIndex(fields=['search_vector'], name='post_search_idx'),
        ]

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)