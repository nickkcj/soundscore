import pytest
import uuid

@pytest.fixture
def user_factory():
    """Factory for creating test users"""
    def create_user(username=None, email=None, password="testpass123"):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Generate unique username and email if not provided
        if username is None:
            username = f"testuser_{uuid.uuid4().hex[:8]}"
        if email is None:
            email = f"test_{uuid.uuid4().hex[:8]}@example.com"
            
        return User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
    return create_user

@pytest.fixture
def album_factory():
    """Factory for creating test albums"""
    def create_album(title=None, artist="Test Artist", spotify_id=None):
        from apps.reviews.models import Album
        
        # Generate unique values if not provided
        if title is None:
            title = f"Test Album {uuid.uuid4().hex[:8]}"
        if spotify_id is None:
            spotify_id = f"spotify_{uuid.uuid4().hex[:8]}"
            
        return Album.objects.create(
            title=title,
            artist=artist,
            spotify_id=spotify_id,
            cover_image="http://example.com/cover.jpg"
        )
    return create_album

@pytest.fixture
def review_factory():
    """Factory for creating test reviews"""
    def create_review(user, album, rating=5, text="Great album!"):
        from apps.reviews.models import Review
        return Review.objects.create(
            user=user,
            album=album,
            rating=rating,
            text=text
        )
    return create_review

@pytest.fixture
def group_factory():
    """Factory for creating test groups"""
    def create_group(name=None, creator=None, creator_username=None):
        from django.contrib.auth import get_user_model
        from apps.groups.models import Group
        User = get_user_model()
        
        # Generate unique name if not provided
        if name is None:
            name = f"Test Group {uuid.uuid4().hex[:8]}"
            
        # Handle creator
        if creator is None and creator_username is not None:
            creator = User.objects.get(username=creator_username)
        elif creator is None:
            # Create a new user if no creator provided
            creator = User.objects.create_user(
                username=f"creator_{uuid.uuid4().hex[:8]}",
                email=f"creator_{uuid.uuid4().hex[:8]}@example.com",
                password="testpass123"
            )
            
        return Group.objects.create(
            name=name,
            description="Test group description",
            category="music",
            privacy="public",
            creator=creator
        )
    return create_group