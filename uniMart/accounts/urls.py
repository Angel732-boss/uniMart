from django.urls import path, include 
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from .views import UserCreateView, UserLoginView

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path('login/', UserLoginView.as_view(), name="accounts-login"),
    path('register/', UserCreateView.as_view(), name="accounts-register"),
    path('sitemap.xml', sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap")
]