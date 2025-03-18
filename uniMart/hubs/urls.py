from django.urls import path
from .views import home, about, test_url

urlpatterns = [
    path('', home, name="home"),
    path('about/', about, name="about"),
    path('test_ip/', test_url, name='ip')
]