import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uniMart.settings')

app = Celery('uniMart')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-event-statuses-every-5-minutes': {
        'task': 'events.tasks.update_event_statuses',
        'schedule': 300.0,  # 300 seconds = 5 minutes
    },
    'update-event-search_vectors-every-5-minutes': {
        'task': 'events.tasks.update_event_search_vectors',
        'schedule': 300.0,  # 300 seconds = 5 minutes
    },
}
