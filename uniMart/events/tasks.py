from celery import shared_task
from django.core.management import call_command
from django.contrib.postgres.search import SearchVector

@shared_task
def update_event_statuses():
    call_command('update_event_statuses')

@shared_task
def update_search_vector(pk):
    from .models import Event
    Event.objects.filter(pk=pk).update(
        search_vector=SearchVector('name', 'venue', 'description')
    )