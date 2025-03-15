from django.shortcuts import render, HttpResponse
from utils.models import About
# Create your views here.

clients = [
    'assets/img/clients/client-1.png',
    'assets/img/clients/client-2.png',
    'assets/img/clients/client-3.png',
    'assets/img/clients/client-4.png',
    'assets/img/clients/client-5.png',
    'assets/img/clients/client-6.png'
]

def home(request):
    contexts = {
        "clients": clients,
        "abouts": About.objects.all()
    }
    return render(request, "hubs/home.html", contexts)

def test_url(request):
    return HttpResponse(f"REMOTE_ADDR: {request.META.get('REMOTE_ADDR')}")