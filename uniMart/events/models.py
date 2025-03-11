from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import User
from utils.models import TimeStampedModel
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

# Create your models here.

class Event(TimeStampedModel):
    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    attendees = models.ManyToManyField(User, related_name='events_attending', blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    search_vector = models.SearchVectorField(null=True)
    slug = models.SlugField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )
    description = models.TextField(null=True)
    meta_keywords = models.CharField('Meta Keywords', null=True, max_length=255, help_text='Comma delimited set of SEO keywords for meta tag')
    meta_description = models.CharField('Meta Description', null=True, max_length=255, help_text='Content for description meta tag')

    class Meta:
        unique_together = ('hub', 'slug')  # Ensures slug is unique per hub
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
            models.Index(fields=['status']),
            GinIndex(fields=['search_vector'], name='post_search_idx'),
        ]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.start_time.strftime('%Y%m%d')}")

        if not self.pk:  # Only for new events
            now = timezone.now()
            if self.start_time > now:
                self.status = 'planned'
            elif self.start_time <= now < self.end_time:
                self.status = 'ongoing'
            elif self.end_time <= now:
                self.status = 'completed'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Event from {self.start_time} to {self.end_time} - {self.status}"