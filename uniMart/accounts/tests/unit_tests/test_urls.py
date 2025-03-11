from django.test import SimpleTestCase
from django.urls import reverse, resolve
from accounts.views import UserCreateView, UserLoginView

class TestUrls(SimpleTestCase):
    def test_user_accounts_register_url_is_resolved(self):
        url = reverse("accounts-register")
        self.assertEqual(resolve(url).func.view_class, UserCreateView)

    def test_user_accounts_login_url_is_resolved(self):
        url = reverse("accounts-login")
        self.assertEqual(resolve(url).func.view_class, UserLoginView)