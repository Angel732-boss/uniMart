from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import User
from utils.models import TimeStampedModel

class Hub(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    location = models.CharField(max_length=100)
    admin = models.ForeignKey(User, related_name='administered_hub', on_delete=models.PROTECT, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Hub.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name