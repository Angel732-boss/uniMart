from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.test import Client, TestCase, RequestFactory
from accounts.models import User

class TestViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.data = {
            "username": "testuser",
            "password": "@testUser732",
            "email": "testuser@gmail.com",
            "date_of_birth": "2003-08-23",
            "image": "/sites/uniMart/media/profile_pics/default.jpg"
        }

        self.user = User.objects.create(
            username=self.data["username"], 
            password=self.data["password"], 
            email=self.data["email"],
            date_of_birth=self.data["date_of_birth"],
            image=self.data["image"]
        )
        self.register_url = reverse("accounts-register")
        self.login_url = reverse("accounts-login")

    def test_register_view_GET(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    def test_login_view_POST(self):
        response = self.client.post(self.login_url, {'email': self.data['email'], 'password': self.data['password']})
        self.assertEqual(response.status_code, 200)

    def test_login_view_GET(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.user.delete()