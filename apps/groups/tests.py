import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.groups.models import Group, GroupMember
from apps.groups.services.group_service import create_group, join_group

User = get_user_model()

class TestGroupServices:
    """Test group service functions"""
    
    @pytest.mark.django_db
    def test_create_group_success(self, user_factory):
        """Test successful group creation"""
        user = user_factory(username="creator")
        
        group_id = create_group(
            name="Test Group",
            description="Test description",
            category="music",
            privacy="public",
            cover_image_file=None,
            username=user.username,
        )
        
        assert isinstance(group_id, int)
        
        # Verify group was created
        group = Group.objects.get(id=group_id)
        assert group.name == "Test Group"


