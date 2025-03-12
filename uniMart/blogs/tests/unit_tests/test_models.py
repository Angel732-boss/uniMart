from django.test import TestCase
from django.contrib.auth import get_user_model
from blogs.models import Post
from hubs.models import Hub
from utils.models import Category, Tag
from django.contrib.postgres.search import SearchQuery

User = get_user_model()

class PostModelTest(TestCase):
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
        self.hub = Hub.objects.create(name='Tech Hub', location='Owerri Imo State')
        self.category = Category.objects.create(name='Programming')
        self.post = Post.objects.create(
            title='Django Basics',
            content='Learning Django is fun!',
            author=self.user,
            hub=self.hub,
            category=self.category,
            slug='django-basics'
        )
        self.tag = Tag.objects.create(name='django')
        self.post.tags.add(self.tag)

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Django Basics')
        self.assertEqual(self.post.content, 'Learning Django is fun!')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.hub, self.hub)
        self.assertEqual(self.post.category, self.category)
        self.assertEqual(self.post.slug, 'django-basics')

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            Post.objects.create(
                title='Another Post',
                content='Content here',
                author=self.user,
                hub=self.hub,
                category=self.category,
                slug='django-basics'
            )

    def test_search_vector_update(self):
        post = Post.objects.get(id=self.post.id)
        self.assertTrue(post.search_vector)
        results = Post.objects.filter(search_vector=SearchQuery('django'))
        self.assertIn(post, results)

    def test_tags_relationship(self):
        self.assertIn(self.tag, self.post.tags.all())
        self.assertEqual(self.post.tags.count(), 1)

    def test_author_cascade(self):
        self.user.delete()
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())