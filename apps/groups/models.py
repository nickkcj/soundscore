from django.db import models
from apps.users.models import User

# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    privacy = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='public')
    category = models.CharField(max_length=50, blank=True, null=True)  # Optional category for the group
    cover_image = models.ImageField(upload_to='group_covers/', blank=True, null=True)  # Optional cover image
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
        
    class Meta:
        db_table = 'soundscore_group'

class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    date_joined = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'soundscore_group_member'
        unique_together = ('group', 'user')
        
    def __str__(self):
        return f"{self.user.username} in {self.group.name}"
    

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'soundscore_group_message'
        
    def __str__(self):
        return f"Message from {self.user.username} in {self.group.name}"
