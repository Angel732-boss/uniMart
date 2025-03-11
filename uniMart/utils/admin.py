from django.contrib import admin
from .models import SearchHistory, Tag, Category

# Register your models here.
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(SearchHistory)