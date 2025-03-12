from django.test import TestCase
from accounts.models import User

class TestModels(TestCase):

    def setUp(self):
        self.data = {
            "username": "testuser",
            "password": "@testUser732",
            "email": "testuser@gmail.com",
            "date_of_birth": "2003-08-23",
            "image": "/apps/media/profile_pics/default.jpg"
        }

        self.user = User.objects.create(
            username=self.data["username"], 
            password=self.data["password"], 
            email=self.data["email"],
            date_of_birth=self.data["date_of_birth"],
            image=self.data["image"]
        )

    def test_user_account_data(self):
        self.assertEqual(self.user.username, self.data["username"])
        self.assertEqual(self.user.email, self.data["email"])
        self.assertEqual(self.user.date_of_birth, self.data["date_of_birth"])
        self.assertEqual(self.user.image.path, self.data["image"])

    def tearDown(self):
        self.user.delete()