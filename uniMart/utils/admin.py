from django.contrib import admin
from .models import SearchHistory, Tag, Category, About, Client#, Brand

# Register your models here.
admin.site.register(Tag)
#admin.site.register(Brand)
admin.site.register(Client)
admin.site.register(About)
admin.site.register(Category)
admin.site.register(SearchHistory)