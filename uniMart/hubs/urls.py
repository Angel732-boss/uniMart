from django.urls import path
from .views import home, test_url

urlpatterns = [
    path('', home, name="home"),
    path('test_ip/', test_url, name='ip')
]