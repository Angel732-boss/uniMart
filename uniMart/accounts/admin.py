from .models import User
from .forms import UserRegisterForm
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    add_form = UserRegisterForm

    list_display = ["username", "email", "date_of_birth", "is_active", "is_superuser"]
    list_filter = ["is_active", "is_superuser"]
    fieldsets = [
        (None, {"fields": ["username", "email", "password", "hub"]}),
        ("Personal info", {"fields": ["image", "date_of_birth"]}),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "email", "hub", "date_of_birth", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["username", "email"]
    ordering = ["email"]
    filter_horizontal = []

# Register your models here.
admin.site.register(User, UserAdmin)