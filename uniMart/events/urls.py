from django.urls import path
from .views import home, attend_event

urlpatterns = [
    path('', home, name="event-home"),
    path('attend/<int:event_id>/', attend_event, name='attend_event'),
]