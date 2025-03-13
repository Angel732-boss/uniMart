from django.test import TestCase
from django.utils import timezone
from events.models import Event
from hubs.models import Hub
from accounts.models import User  # Assuming User is in accounts app
from datetime import timedelta
from django.contrib.postgres.search import SearchQuery
from django.utils.text import slugify

class EventModelTest(TestCase):
    def setUp(self):
        """
        Set up initial test data: an organizer, an attendee, a hub, and an event.
        The event's start_time is in the future, so its status should be 'planned'.
        """
        # Create an organizer user
        self.organizer = User.objects.create(
            username='organizer',
            password='password',
            email='organizer@example.com',
            date_of_birth='1990-01-01',
            image='/apps/media/profile_pics/default.jpg'
        )
        # Create an attendee user
        self.attendee = User.objects.create(
            username='attendee',
            password='password',
            email='attendee@example.com',
            date_of_birth='1990-01-01',
            image='/apps/media/profile_pics/default.jpg'
        )
        # Create a hub
        self.hub = Hub.objects.create(name='Test Hub', location='Test Location')
        
        # Define times for the event
        now = timezone.now()
        self.start_time = now + timedelta(days=1)
        self.end_time = now + timedelta(days=2)
        
        # Create an event without specifying a slug (should be auto-generated)
        self.event = Event.objects.create(
            name='Test Event',
            organizer=self.organizer,
            hub=self.hub,
            start_time=self.start_time,
            end_time=self.end_time,
            description='This is a test event.',
        )
        # Add the attendee to the event
        self.event.attendees.add(self.attendee)

    ### Basic Field and Creation Tests ###
    def test_event_creation(self):
        """Test that an event is created correctly with all fields set as expected."""
        self.assertEqual(self.event.name, 'Test Event')
        self.assertEqual(self.event.organizer, self.organizer)
        self.assertEqual(self.event.hub, self.hub)
        self.assertEqual(self.event.start_time, self.start_time)
        self.assertEqual(self.event.end_time, self.end_time)
        self.assertEqual(self.event.description, 'This is a test event.')
        self.assertEqual(self.event.status, 'planned')  # Since start_time is in the future
        # Check auto-generated slug
        expected_slug = slugify(f"{self.event.name}-{self.start_time.strftime('%Y%m%d')}")
        self.assertEqual(self.event.slug, expected_slug)
        # Check timestamps
        self.assertIsNotNone(self.event.created_at)
        self.assertIsNotNone(self.event.updated_at)
        # Check default fields
        self.assertTrue(self.event.is_active)
        self.assertIsNone(self.event.meta_keywords)
        self.assertIsNone(self.event.meta_description)

    ### Unique Constraint Tests ###
    def test_unique_together_constraint(self):
        """Test that creating an event with the same hub and slug raises an exception."""
        with self.assertRaises(Exception):  # Typically IntegrityError
            Event.objects.create(
                name='Another Event',
                organizer=self.organizer,
                hub=self.hub,
                start_time=self.start_time,
                end_time=self.end_time,
                slug=self.event.slug  # Same slug and hub as self.event
            )

    def test_slug_unique_per_hub(self):
        """Test that the same slug can be used in a different hub."""
        another_hub = Hub.objects.create(name='Another Hub', location='Another Location')
        another_event = Event.objects.create(
            name='Test Event',
            organizer=self.organizer,
            hub=another_hub,  # Different hub
            start_time=self.start_time,
            end_time=self.end_time,
        )
        self.assertEqual(another_event.slug, self.event.slug)  # Same slug is allowed

    ### Status Logic Tests ###
    def test_status_planned(self):
        """Test that an event with a future start_time gets 'planned' status."""
        future_start = timezone.now() + timedelta(days=3)
        future_end = future_start + timedelta(hours=2)
        event = Event.objects.create(
            name='Future Event',
            organizer=self.organizer,
            hub=self.hub,
            start_time=future_start,
            end_time=future_end,
        )
        self.assertEqual(event.status, 'planned')

    def test_status_ongoing(self):
        """Test that an event with start_time in the past and end_time in the future gets 'ongoing' status."""
        now = timezone.now()
        past_start = now - timedelta(hours=1)
        future_end = now + timedelta(hours=1)
        event = Event.objects.create(
            name='Ongoing Event',
            organizer=self.organizer,
            hub=self.hub,
            start_time=past_start,
            end_time=future_end,
        )
        self.assertEqual(event.status, 'ongoing')

    def test_status_completed(self):
        """Test that an event with both times in the past gets 'completed' status."""
        past_start = timezone.now() - timedelta(days=2)
        past_end = past_start + timedelta(hours=2)
        event = Event.objects.create(
            name='Past Event',
            organizer=self.organizer,
            hub=self.hub,
            start_time=past_start,
            end_time=past_end,
        )
        self.assertEqual(event.status, 'completed')

    def test_status_canceled(self):
        """Test that an event can be manually set to 'canceled' status."""
        event = Event.objects.create(
            name='Canceled Event',
            organizer=self.organizer,
            hub=self.hub,
            start_time=self.start_time,
            end_time=self.end_time
        )
        event.status = 'canceled'
        event.save()
        self.assertEqual(event.status, 'canceled')
    '''
    ### Search Vector Tests ###
    def test_search_vector_creation(self):
        """Test that the search_vector is populated on event creation."""
        event = Event.objects.get(id=self.event.id)
        self.assertTrue(event.search_vector)  # Should be non-null due to trigger
    '''

    def test_search_vector_search(self):
        """Test that searching via search_vector returns the correct event."""
        results = Event.objects.filter(search_vector=SearchQuery('test'))
        self.assertIn(self.event, results)
        results = Event.objects.filter(search_vector=SearchQuery('event'))
        self.assertIn(self.event, results)
        results = Event.objects.filter(search_vector=SearchQuery('randomword'))
        self.assertNotIn(self.event, results)

    def test_search_vector_update(self):
        """Test that updating name and description updates the search_vector."""
        self.event.name = 'Updated Event'
        self.event.description = 'This is an updated event.'
        self.event.save()
        updated_event = Event.objects.get(id=self.event.id)
        results = Event.objects.filter(search_vector=SearchQuery('updated'))
        self.assertIn(updated_event, results)
        results = Event.objects.filter(search_vector=SearchQuery('test'))
        self.assertNotIn(updated_event, results)  # 'test' no longer in name or description

    ### Relationship Tests ###
    def test_attendees_relationship(self):
        """Test adding and removing attendees via the many-to-many relationship."""
        self.assertIn(self.attendee, self.event.attendees.all())
        self.assertEqual(self.event.attendees.count(), 1)
        # Add another attendee
        another_attendee = User.objects.create(
            username='another_attendee',
            password='password',
            email='another@example.com',
            date_of_birth='1990-01-01',
            image='/apps/media/profile_pics/default.jpg'
        )
        self.event.attendees.add(another_attendee)
        self.assertEqual(self.event.attendees.count(), 2)
        # Remove the original attendee
        self.event.attendees.remove(self.attendee)
        self.assertEqual(self.event.attendees.count(), 1)
        self.assertNotIn(self.attendee, self.event.attendees.all())

    def test_organizer_cascade(self):
        """Test that deleting the organizer deletes the event (cascade)."""
        organizer_id = self.organizer.id
        self.organizer.delete()
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())
        self.assertFalse(User.objects.filter(id=organizer_id).exists())

    def test_hub_cascade(self):
        """Test that deleting the hub deletes the event (cascade)."""
        hub_id = self.hub.id
        self.hub.delete()
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())
        self.assertFalse(Hub.objects.filter(id=hub_id).exists())

    def test_attendee_delete(self):
        """Test that deleting an attendee doesn't delete the event but removes the relationship."""
        attendee_id = self.attendee.id
        self.attendee.delete()
        self.assertTrue(Event.objects.filter(id=self.event.id).exists())  # Event still exists
        self.assertFalse(User.objects.filter(id=attendee_id).exists())
        self.assertEqual(self.event.attendees.count(), 0)

    ### Meta Options and Ordering Tests ###
    def test_ordering(self):
        """Test that events are ordered by created_at descending."""
        another_event = Event.objects.create(
            name='Another Event',
            organizer=self.organizer,
            hub=self.hub,
            start_time=self.start_time + timedelta(days=1),
            end_time=self.end_time + timedelta(days=1),
        )
        events = Event.objects.all()
        self.assertEqual(events[0], another_event)  # Latest created_at first
        self.assertEqual(events[1], self.event)

    ### Custom Behavior Tests ###
    def test_slug_provided(self):
        """Test that providing a custom slug uses it instead of generating one."""
        custom_slug = 'custom-slug'
        event = Event.objects.create(
            name='Custom Event',
            organizer=self.organizer,
            hub=self.hub,
            start_time=self.start_time,
            end_time=self.end_time,
            slug=custom_slug,
        )
        self.assertEqual(event.slug, custom_slug)

    def test_meta_fields(self):
        """Test setting optional meta_keywords and meta_description fields."""
        event = Event.objects.create(
            name='Meta Event',
            organizer=self.organizer,
            hub=self.hub,
            start_time=self.start_time,
            end_time=self.end_time,
            meta_keywords='event, test, django',
            meta_description='This is a test event for meta fields.',
        )
        self.assertEqual(event.meta_keywords, 'event, test, django')
        self.assertEqual(event.meta_description, 'This is a test event for meta fields.')

    def test_is_active(self):
        """Test the is_active field behavior."""
        self.assertTrue(self.event.is_active)  # Default is True
        self.event.is_active = False
        self.event.save()
        updated_event = Event.objects.get(id=self.event.id)
        self.assertFalse(updated_event.is_active)

    def test_str_method(self):
        """Test the __str__ method returns the expected string."""
        expected_str = f"Event from {self.event.start_time} to {self.event.end_time} - {self.event.status}"
        self.assertEqual(str(self.event), expected_str)
