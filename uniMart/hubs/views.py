from django.shortcuts import render, HttpResponse

# Create your views here.

def home(request):
    return HttpResponse(f"REMOTE_ADDR: {request.META.get('REMOTE_ADDR')}")