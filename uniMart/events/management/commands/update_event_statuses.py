from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event

class Command(BaseCommand):
    help = 'Updates the status of all events based on the current time'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Update events that are 'planned' and have started to 'ongoing'
        Event.objects.filter(
            status='planned',
            start_time__lte=now
        ).update(status='ongoing')
        
        # Update events that are 'ongoing' and have ended to 'completed'
        Event.objects.filter(
            status='ongoing',
            end_time__lte=now
        ).update(status='completed')
        
        self.stdout.write(self.style.SUCCESS('Successfully updated event statuses'))