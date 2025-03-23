import os
from uuid import uuid4
from django.db import models
from django.utils.text import slugify
from accounts.models import User

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class LastProcessed(models.Model):
    task_name = models.CharField(max_length=100, unique=True)
    last_timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.task_name}: {self.last_timestamp}"

class Tag(TimeStampedModel):
    name = models.CharField(max_length=50)
    hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE, related_name='tags', null=True, blank=True)

    def __str__(self):
        return self.name

from django.db import models
from django.utils.text import slugify

class Category(TimeStampedModel):
    # Define choices for service types
    SERVICE_TYPE_CHOICES = [
        ('events', 'Events'),
        ('services', 'Services'),
        ('blogs', 'Blogs'),
        ('communities', 'Communities')
    ]

    name = models.CharField(max_length=50)
    hub = models.ForeignKey(
        'hubs.Hub',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categories',
        help_text="If set, this category is specific to a hub; if null, it’s global."
    )
    
    # New service_type field
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPE_CHOICES,
        help_text="The type of service this category belongs to."
    )
    slug = models.SlugField(
        max_length=50,
        help_text="A URL-friendly version of the name.",
        blank=True
    )
    description = models.TextField(null=True)
    meta_keywords = models.CharField(
        'Meta Keywords',
        null=True,
        blank=True,
        max_length=255,
        help_text='Comma delimited set of SEO keywords for meta tag'
    )
    meta_description = models.CharField(
        'Meta Description',
        null=True,
        blank=True,
        max_length=255,
        help_text='Content for description meta tag'
    )

    class Meta:
        # Updated uniqueness constraint
        unique_together = ('hub', 'service_type', 'slug')
        verbose_name_plural = "categories"
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        # Updated to include service type
        return f"{self.get_service_type_display()} - {self.name}"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE, related_name='searches')
    ipaddress = models.GenericIPAddressField()
    tracking_id = models.UUIDField()

    class Meta:
        verbose_name_plural = "Search Histories"

    def __str__(self):
        username = 'ananymous'
        if self.user:
            username = self.user.username
        return f"{username} searched '{self.query}' in {self.hub.name}"

def rename(instance, filename):
    upload_to = f'clients/{instance.name}/'
    ext = filename.split('.')[-1]
    return os.path.join(upload_to, f'{uuid4().hex}.{ext}')

class Client(TimeStampedModel):
    name = models.CharField(max_length=100)
    url = models.URLField()
    image = models.ImageField(upload_to=rename)

    def __str__(self):
        return self.name

class About(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField()
    position = models.PositiveIntegerField(unique=True, null=True, blank=True)
    url = models.URLField(blank=True, unique=True, null=True)
    header = models.BooleanField(default=False)

    class Meta:
        ordering = ["-position"]

    def __str__(self):
        return self.name

'''
class Brand(TimeStampedModel):
    url = models.URLField()
    name = models.CharField(max_length=20)
    content = models.TextField()
    icon = models.CharField()

    def __str__(self):
        return self.name
'''