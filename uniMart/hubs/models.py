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
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name