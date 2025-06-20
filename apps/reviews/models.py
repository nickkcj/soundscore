from django.db import models
from apps.users.models import User

class Album(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True, null=True)  
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    cover_image = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} by {self.artist}"

    class Meta:
        db_table = 'soundscore_album'

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_favorite = models.BooleanField(default=False)  # For marking favorite albums
    
    class Meta:
        db_table = 'soundscore_review'
        # Ensure a user can only review an album once
        unique_together = ('user', 'album')
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.album.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.review.id}"

    class Meta:
        db_table = 'soundscore_comment'

class ReviewLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_likes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'soundscore_review_like'
        unique_together = ('user', 'review')

    def __str__(self):
        return f"{self.user.username} likes {self.review.id}"