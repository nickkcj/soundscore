from django.db import models
from apps.users.models import User
from apps.reviews.models import Review
from apps.reviews.models import Comment  # Adjust import if Comment is in another app

class Notification(models.Model):
    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    actor = models.ForeignKey(User, related_name='notifications_sent', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    review = models.ForeignKey(Review, null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notification"
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient_id}: {self.message[:30]}"
