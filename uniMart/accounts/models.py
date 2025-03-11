import os
from uuid import uuid4
from django.db import models
from PIL import Image
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.

def rename(instance, filename):
    upload_to = f'profile_pics/{instance.username}/'
    ext = filename.split('.')[-1]
    return os.path.join(upload_to, f'{uuid4().hex}.{ext}')

class User(AbstractUser):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]
    email = models.EmailField(unique=True, max_length=254, help_text="Required. Must provide a valid email address.", verbose_name='email address')
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=False,  # Not allowing the field to be blank
    )
    date_of_birth = models.DateField(blank=False, help_text="Required.", verbose_name="date of birth")
    hub = models.ForeignKey('hubs.Hub', on_delete=models.PROTECT, null=True, related_name='users')
    image = models.ImageField(
        default="profile_pics/default.jpg", 
        upload_to=rename
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        related_name='custom_user_group'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        related_name='custom_user_group'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'date_of_birth']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)