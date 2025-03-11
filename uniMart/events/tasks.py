from celery import shared_task
from django.core.management import call_command

@shared_task
def update_event_statuses():
    call_command('update_event_statuses')