class Community(models.Model):
    # ... other fields ...
    search_vector = models.SearchVectorField(null=True)

# Migration for trigger
operations = [
    RunSQL("""
        CREATE TRIGGER community_search_vector_update
        BEFORE INSERT OR UPDATE ON public.community
        FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(search_vector, 'pg_catalog.english', name);
    """, """
        DROP TRIGGER community_search_vector_update ON public.community;
    """),
]

from django.contrib.postgres.search import SearchQuery, SearchRank

def get_related_events(service, user_hub, limit=3):
    query = SearchQuery(service.name)
    return Event.objects.filter(
        hub=user_hub,
        status__in=['planned', 'ongoing']
    ).annotate(rank=SearchRank('search_vector', query)).order_by('-rank')[:limit]

category_queryset = Category.objects.filter(hub=event.hub) | Category.objects.filter(hub__isnull=True)
tag_queryset = Tag.objects.filter(hub=event.hub) | Tag.objects.filter(hub__isnull=True)

if admin_user.profile.current_hub != community.hub:
    raise ValidationError("Admin must be from the same hub as the community.")


user = User.objects.get(id=1)
administered_communities = user.administered_communities.all()

# utils.py
from django.db.models import Q
from .models import SearchHistory, Event, Service, Community

def get_recommendations(user, limit=3):
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return {'events': [], 'services': [], 'communities': []}

    hub = user.profile.current_hub
    if not hub:
        return {'events': [], 'services': [], 'communities': []}

    # Get user's recent search queries (e.g., last 10)
    searches = SearchHistory.objects.filter(user=user, hub=hub).order_by('-timestamp')[:10]
    if not searches:
        return {'events': [], 'services': [], 'communities': []}

    # Extract keywords from search queries
    keywords = [search.query for search in searches]
    search_query = SearchQuery(' '.join(keywords))

    # Recommend Events
    events = Event.objects.filter(
        hub=hub,
        status__in=['planned', 'ongoing'],
        search_vector=search_query
    ).annotate(rank=SearchRank('search_vector', search_query)).order_by('-rank')[:limit]

    # Recommend Services
    services = Service.objects.filter(
        hub=hub,
        search_vector=search_query
    ).annotate(rank=SearchRank('search_vector', search_query)).order_by('-rank')[:limit]

    # Recommend Communities
    communities = Community.objects.filter(
        hub=hub,
        search_vector=search_query
    ).annotate(rank=SearchRank('search_vector', search_query)).order_by('-rank')[:limit]

    return {
        'events': events,
        'services': services,
        'communities': communities,
    }

def get_related_events(service, user_hub, limit=3):
    query = SearchQuery(service.name)
    return Event.objects.filter(
        hub=user_hub,
        status__in=['planned', 'ongoing']
    ).annotate(rank=SearchRank('search_vector', query)).order_by('-rank')[:limit]

# views.py
from django.shortcuts import render
from django.contrib.postgres.search import SearchQuery, SearchRank
from .models import Event, Service, SearchHistory

def search(request):
    query = request.GET.get('q', '').strip()
    user = request.user
    hub = user.profile.current_hub if user.is_authenticated and hasattr(user, 'profile') else None

    if query and user.is_authenticated and hub:
        # Save the search query
        SearchHistory.objects.create(user=user, query=query, hub=hub)

    # Perform full text search
    search_query = SearchQuery(query)
    events = Event.objects.filter(
        hub=hub,
        search_vector=search_query
    ).annotate(rank=SearchRank('search_vector', search_query)).order_by('-rank')
    services = Service.objects.filter(
        hub=hub,
        search_vector=search_query
    ).annotate(rank=SearchRank('search_vector', search_query)).order_by('-rank')

    return render(request, 'search_results.html', {
        'query': query,
        'events': events,
        'services': services,
    })

Post.objects.update(search_vector=SearchVector('title', weight='A') + SearchVector('content', weight='B'))

from django.contrib.postgres.search import SearchQuery
Article.objects.filter(search_vector=SearchQuery('django'))

EXPLAIN ANALYZE SELECT * FROM articles WHERE search_vector @@ to_tsquery('django');

REINDEX INDEX search_vector_idx;

SELECT * FROM articles WHERE search_vector @@ to_tsquery('django & python');

<form method="get">
    <input type="text" name="q" value="{{ request.GET.q }}">
    <button type="submit">Search</button>
</form>
<ul>
{% for article in object_list %}
    <li>{{ article.title }} (Rank: {{ article.rank|floatformat:2 }})</li>
{% empty %}
    <li>No results found.</li>
{% endfor %}
</ul>

from django.views.generic import ListView
from django.contrib.postgres.search import SearchQuery, SearchRank
from myapp.models import Article

class ArticleSearchView(ListView):
    model = Article
    template_name = 'articles/search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            search_query = SearchQuery(query)
            rank = SearchRank('search_vector', search_query)
            return Article.objects.annotate(rank=rank).filter(search_vector=search_query).order_by('-rank')
        return Article.objects.all()

from django.contrib.postgres.search import SearchQuery, SearchRank

# Basic search
query = SearchQuery('django')
results = Article.objects.filter(search_vector=query)

# Search with ranking (sort by relevance)
rank = SearchRank('search_vector', query)
results = Article.objects.annotate(rank=rank).filter(search_vector=query).order_by('-rank')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'web_app'),
        'USER': os.getenv('DB_USER', 'postgresadmin'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'admin123'),
        'HOST': os.getenv('DB_HOST', 'postgres_primary'),
        'PORT': os.getenv('DB_PORT', '5432'),
        "OPTIONS": {
            "pool": True,
        },
    },
    
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'web_app'),
        'USER': os.getenv('DB_USER', 'postgresadmin'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'admin123'),
        'HOST': os.getenv('DB_HOST1', 'postgres_replica'),
        'PORT': os.getenv('DB_PORT', '5432'),
        "OPTIONS": {
            "pool": True,
        },
    },

    'replica-2': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'web_app'),
        'USER': os.getenv('DB_USER', 'postgresadmin'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'admin123'),
        'HOST': os.getenv('DB_HOST2', 'postgres_replica2'),
        'PORT': os.getenv('DB_PORT', '5432'),
        "OPTIONS": {
            "pool": True,
        },
    }
}

from django.test import TestCase
from django.db.utils import IntegrityError
from utils.models import Category
from hubs.models import Hub

class CategoryModelTest(TestCase):
    def setUp(self):
        # Create two Hub instances for testing uniqueness across different hubs
        self.hub1 = Hub.objects.create(name='Hub 1')
        self.hub2 = Hub.objects.create(name='Hub 2')
        
        # Create a Category instance with all fields specified
        self.category = Category.objects.create(
            name='Test Category',
            hub=self.hub1,
            service_type='events',
            slug='test-category',
            description='This is a test category.',
            meta_keywords='test, category',
            meta_description='Test category meta description'
        )

    def test_category_creation(self):
        """Test that a Category instance is created with all fields set correctly."""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.hub, self.hub1)
        self.assertEqual(self.category.service_type, 'events')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertEqual(self.category.description, 'This is a test category.')
        self.assertEqual(self.category.meta_keywords, 'test, category')
        self.assertEqual(self.category.meta_description, 'Test category meta description')

    def test_slug_auto_generation(self):
        """Test that the slug is auto-generated when not provided."""
        category = Category.objects.create(
            name='Another Category',
            hub=self.hub1,
            service_type='services'
        )
        self.assertEqual(category.slug, 'another-category')

    def test_unique_together_constraint_same_hub_service_type_slug(self):
        """Test that the uniqueness constraint prevents duplicate (hub, service_type, slug) combinations."""
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name='Duplicate Category',
                hub=self.hub1,
                service_type='events',
                slug='test-category'
            )

    def test_unique_together_constraint_different_hub(self):
        """Test that a category with the same service_type and slug but different hub can be created."""
        category = Category.objects.create(
            name='Test Category',
            hub=self.hub2,
            service_type='events',
            slug='test-category'
        )
        self.assertEqual(category.slug, 'test-category')

    def test_unique_together_constraint_different_service_type(self):
        """Test that a category with the same hub and slug but different service_type can be created."""
        category = Category.objects.create(
            name='Test Category',
            hub=self.hub1,
            service_type='services',
            slug='test-category'
        )
        self.assertEqual(category.slug, 'test-category')

    def test_unique_together_constraint_different_slug(self):
        """Test that a category with the same hub and service_type but different slug can be created."""
        category = Category.objects.create(
            name='Different Slug Category',
            hub=self.hub1,
            service_type='events',
            slug='different-slug'
        )
        self.assertEqual(category.slug, 'different-slug')

    def test_global_category_uniqueness(self):
        """Test that multiple global categories (hub=None) with the same service_type and slug can coexist."""
        category1 = Category.objects.create(
            name='Global Category 1',
            hub=None,
            service_type='events',
            slug='global-category'
        )
        category2 = Category.objects.create(
            name='Global Category 2',
            hub=None,
            service_type='events',
            slug='global-category'
        )
        self.assertNotEqual(category1.id, category2.id)
        self.assertEqual(
            Category.objects.filter(slug='global-category', service_type='events', hub=None).count(),
            2
        )

    def test_str_method(self):
        """Test that the __str__ method returns the expected string."""
        self.assertEqual(str(self.category), 'Events - Test Category')

@shared_task
def resize_image(image_path, bucket_name='my-bucket'):
    import boto3
    from io import BytesIO
    
    s3 = boto3.client('s3')
    
    # Download from S3
    file_obj = BytesIO()
    s3.download_fileobj(bucket_name, image_path, file_obj)
    file_obj.seek(0)
    
    # Resize
    img = Image.open(file_obj)
    if img.height > 300 or img.width > 300:
        img.thumbnail((300, 300))
        output = BytesIO()
        img.save(output, format=img.format, quality=95)
        output.seek(0)
        
        # Upload back to S3
        s3.upload_fileobj(output, bucket_name, image_path)

# dumping 
pg_dump -U username -d database_name > dump.sql
psql -U username -d database_name < dump.sql

python manage.py dumpdata --exclude auth.Permission --exclude contenttypes > data.json
python manage.py dumpdata app_name > data.json
python manage.py loaddata data.json