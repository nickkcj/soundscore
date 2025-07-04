import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.reviews.models import Album, Review
from apps.reviews.services.review_service.add_review import add_review
from apps.reviews.services.review_service.edit_review import edit_review

User = get_user_model()

class TestReviewServices:
    """Test review service functions"""
    
    @pytest.mark.django_db
    def test_add_review_success(self, user_factory, album_factory):
        """Test successful review creation"""
        user = user_factory()
        album = album_factory()
        
        result = add_review(
            user_id=user.id,
            album_id=album.spotify_id,
            rating=5,
            album_title=album.title,
            album_artist=album.artist,
            text="Great album!"
        )
        
        assert result["success"] is True
        assert "Review added successfully" in result["message"]
        
        # Verify review was created
        review = Review.objects.get(user=user, album=album)
        assert review.rating == 5
        assert review.text == "Great album!"
    
    @pytest.mark.django_db
    def test_edit_review_success(self, user_factory, album_factory, review_factory):
        """Test editing a review"""
        user = user_factory()
        album = album_factory()
        review = review_factory(user=user, album=album, rating=3, text="Old text")
        
        result = edit_review(review.id, rating=4, text="New text", is_favorite=True)
        
        assert result["success"] is True
        assert "Review updated successfully" in result["message"]
        
        # Verify changes
        review.refresh_from_db()
        assert review.rating == 4
        assert review.text == "New text"
        assert review.is_favorite is True

class TestReviewViews:
    """Test review views"""
    
    @pytest.mark.django_db
    def test_create_review_view_get(self, user_factory):
        """Test GET request to create review view"""
        user = user_factory()
        client = Client()
        client.force_login(user)
        
        response = client.get(reverse('create_review'))
        
        assert response.status_code == 200
