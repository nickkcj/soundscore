import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.users.models import UserRelationship
from apps.users.services.add_user import create_user
from apps.users.services.follow_user import follow_service


User = get_user_model()

class TestUserServices:
    """Test user service functions"""
    
    @pytest.mark.django_db
    def test_create_user_success(self):
        """Test successful user creation"""
        result = create_user("newuser", "new@example.com", "password123")
        
        assert result["success"] is True
        assert result["message"] == "User created successfully"
        assert "user_id" in result
        
        # Verify user was created in database
        user = User.objects.get(username="newuser")
        assert user.email == "new@example.com"
        assert user.check_password("password123")
    
    @pytest.mark.django_db
    def test_create_user_duplicate_username(self):
        """Test user creation with duplicate username"""
        # Create first user
        create_user("testuser", "test1@example.com", "password123")
        
        # Try to create user with same username
        result = create_user("testuser", "test2@example.com", "password123")
        
        assert result["success"] is False
        assert "Username already exists" in result["message"]
    
    @pytest.mark.django_db
    def test_follow_user_success(self, user_factory):
        """Test following a user"""
        user1 = user_factory(username="follower")
        user2 = user_factory(username="followee")
        
        result = follow_service(user1.id, "followee")
        
        assert result["success"] is True
        assert "You are now following followee" in result["message"]
        
        # Verify relationship was created
        assert UserRelationship.objects.filter(
            user_id=user1, following=user2
        ).exists()

class TestUserViews:
    """Test user views"""
    
    @pytest.mark.django_db
    def test_register_view_get(self):
        """Test GET request to register view"""
        client = Client()
        response = client.get(reverse('register'))
        
        assert response.status_code == 200
    
    @pytest.mark.django_db
    def test_user_profile_view(self, user_factory):
        """Test user profile view"""
        user = user_factory(username="profileuser")
        
        client = Client()
        client.force_login(user)
        
        response = client.get(reverse('profile', kwargs={'username': 'profileuser'}))
        
        assert response.status_code == 200
