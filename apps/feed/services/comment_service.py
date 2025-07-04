from apps.reviews.models import Comment
from apps.users.models import User
from apps.reviews.models import Review


def post_comment_service(review_id, text, username, parent_id=None):
    """Post a comment on a review."""

    # Validate user and review input parameters
    user = User.objects.filter(username=username).first()
    if not user:
        raise Exception("User not found")
    review = Review.objects.filter(id=review_id).first()
    if not review:
        raise Exception("Review not found")
    

    # Organize the data being passed to the html
    comment_data = {
        "review": review,
        "user": user,
        "text": text
    }

    # If parent_id is provided, set the parent comment
    if parent_id:
        parent_comment = Comment.objects.filter(id=parent_id).first()
        if parent_comment:
            comment_data["parent"] = parent_comment

    
    # Create the comment
    comment = Comment.objects.create(**comment_data)
    return comment
