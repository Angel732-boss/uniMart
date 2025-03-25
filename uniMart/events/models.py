import os
from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from accounts.models import User
from utils.models import TimeStampedModel
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Event(TimeStampedModel):
    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    attendees = models.ManyToManyField(User, related_name='events_attending', blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    venue = models.CharField(max_length=255, db_index=True)
    capacity = models.PositiveIntegerField(default=100)
    category = models.ForeignKey(
        'utils.Category',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        limit_choices_to={'service_type': 'events'},
        related_name='events'
    )
    search_vector = SearchVectorField(null=True, blank=True)
    slug = models.SlugField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )
    description = models.TextField(null=True, blank=True)
    meta_keywords = models.CharField(null=True, blank=True, max_length=255, help_text='Comma delimited set of SEO keywords for meta tag')
    meta_description = models.CharField(null=True, blank=True, max_length=255, help_text='Content for description meta tag')

    class Meta:
        unique_together = ('hub', 'slug')
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
            models.Index(fields=['status']),
            models.Index(fields=['name']),
            models.Index(fields=['venue']),
            GinIndex(fields=['search_vector'], name='event_search_idx'),
        ]
        ordering = ['-updated_at']

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError('End time must be after start time')
            if self.start_time < timezone.now() and not self.pk:
                raise ValidationError('Cannot create event in the past')

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.start_time.strftime('%Y%m%d')}")
            slug = base_slug
            counter = 1
            while Event.objects.filter(hub=self.hub, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if not self.pk:
            now = timezone.now()
            if self.start_time > now:
                self.status = 'planned'
            elif self.start_time <= now < self.end_time:
                self.status = 'ongoing'
            elif self.end_time <= now:
                self.status = 'completed'
                
        super().save(*args, **kwargs)

    def generate_meta_description(self):
        """Generate a meta description based on available fields."""
        if self.description:
            return self.description[:150]  # Trim to 150 characters
        # Construct a sentence if description is missing
        category_str = f"a {self.category.name} " if self.category else ""
        return f"Join {self.organizer.username} for {self.name}, {category_str}event at {self.venue} on {self.start_time.strftime('%B %d, %Y')}."[:150]

    def generate_meta_keywords(self):
        """Generate a comma-separated list of keywords from related fields."""
        keywords = [self.name, self.venue]
        if self.category:
            keywords.append(self.category.name)
        keywords.extend([self.hub.name, self.organizer.username])
        return ", ".join(keywords)

    @property
    def duration(self):
        return self.end_time - self.start_time
    
    @property
    def thumbnail(self):
        default_thumbnail = self.images.filter(is_thumbnail=True).first()
        if default_thumbnail:
            return default_thumbnail
        default_thumbnail = self.images.first()
        default_thumbnail.is_thumbnail = True
        default_thumbnail.save()
        return default_thumbnail

    @property
    def is_full(self):
        return self.attendees.count() >= self.capacity

    def add_attendee(self, user):
        if self.is_full:
            raise ValidationError("Event is at full capacity.")
        self.attendees.add(user)

    def __str__(self):
        return f"{self.name} ({self.status})"
    
def rename(instance, filename):
    upload_to = f'events/{instance.event.name}/'
    ext = filename.split('.')[-1]
    return os.path.join(upload_to, f'{uuid4().hex}.{ext}')

class EventImage(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=rename, default="events/default.jpg")
    is_thumbnail = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if EventImage.objects.filter(event=self.event).count() == 0:
            self.is_thumbnail = True

        if self.is_thumbnail:
            EventImage.objects.filter(event=self.event).exclude(id=self.id).update(is_thumbnail=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.event.name}"
