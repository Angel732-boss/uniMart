from .models import User
from django.contrib import messages
from .forms import UserRegisterForm
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
#from django.views.decorators.cache import cache_page

# Create your views here.

class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy('accounts-register')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account has been created for {username}...')
        return redirect(self.success_url)


class UserLoginView(LoginView):
    template_name = "accounts/login.html"

