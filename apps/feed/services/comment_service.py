from apps.reviews.models import Comment
from apps.users.models import User
from apps.reviews.models import Review


def post_comment_service(review_id, text, username, parent_id=None):
    user = User.objects.filter(username=username).first()
    if not user:
        raise Exception("User not found")
    review = Review.objects.filter(id=review_id).first()
    if not review:
        raise Exception("Review not found")

    comment_data = {
        "review": review,
        "user": user,
        "text": text
    }
    if parent_id:
        parent_comment = Comment.objects.filter(id=parent_id).first()
        if parent_comment:
            comment_data["parent"] = parent_comment

    comment = Comment.objects.create(**comment_data)
    return comment
