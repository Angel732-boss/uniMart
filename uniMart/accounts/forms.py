from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from datetime import datetime

class UserRegisterForm(UserCreationForm):
    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'max': datetime.now().date()})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'date_of_birth', 'password1', 'password2']