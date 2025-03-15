from django.shortcuts import render
from .models import Post
# Create your views here.

def list(request):
    posts = Post.objects.all()
    return render(request, "blogs/home.html", context={"posts": posts})