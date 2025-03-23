from django.shortcuts import render
from .models import Event
from django.db.models import Count

# Create your views here.

def home(request):
    events = Event.objects.all().select_related('organizer').annotate(attendee_count=Count('attendees'))
    return render(request, template_name="events/home.html", context={"events": events})