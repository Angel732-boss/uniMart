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

def save(self, *args, **kwargs):
    if not self.slug:
        base_slug = slugify(f"{self.name}-{self.start_time.strftime('%Y%m%d')}")
        slug = base_slug
        counter = 1
        while Event.objects.filter(hub=self.hub, slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
    # Rest of the save method...
    super().save(*args, **kwargs)