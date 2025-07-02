from apps.users.models import User, UserRelationship
from django.core.paginator import Paginator

def get_followers_list(username, page=1, per_page=20):
    """Get list of users following this user"""
    try:
        user = User.objects.get(username=username)
        followers_relationships = UserRelationship.objects.filter(
            following=user
        ).select_related('user_id')
        
        followers = [rel.user_id for rel in followers_relationships]
        
        paginator = Paginator(followers, per_page)
        page_obj = paginator.get_page(page)
        
        followers_data = []
        for follower in page_obj:
            profile_picture = follower.profile_picture.url if follower.profile_picture else '/media/profile_pictures/default.jpg'
            followers_data.append({
                'username': follower.username,
                'profile_picture': profile_picture,
            })
        
        return {
            'followers': followers_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
        }
        
    except User.DoesNotExist:
        return {
            'followers': [],
            'has_next': False,
            'has_previous': False,
            'current_page': 1,
            'total_pages': 0,
            'total_count': 0,
        }


def get_following_list(username, page=1, per_page=20):
    """Get list of users this user is following"""
    try:
        user = User.objects.get(username=username)
        following_relationships = UserRelationship.objects.filter(
            user_id=user
        ).select_related('following')
        
        following = [rel.following for rel in following_relationships]
        
        paginator = Paginator(following, per_page)
        page_obj = paginator.get_page(page)
        
        following_data = []
        for followed_user in page_obj:
            profile_picture = followed_user.profile_picture.url if followed_user.profile_picture else '/media/profile_pictures/default.jpg'
            following_data.append({
                'username': followed_user.username,
                'profile_picture': profile_picture,
            })
        
        return {
            'following': following_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
        }
        
    except User.DoesNotExist:
        return {
            'following': [],
            'has_next': False,
            'has_previous': False,
            'current_page': 1,
            'total_pages': 0,
            'total_count': 0,
        }