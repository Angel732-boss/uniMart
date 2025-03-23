from django.contrib import admin
from .models import Event, EventImage

# Register your models here.
class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1  # Number of empty forms to display

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [EventImageInline]

#admin.site.register(Event)
admin.site.register(EventImage)