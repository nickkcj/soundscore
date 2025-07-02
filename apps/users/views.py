from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.users.models import User
from apps.reviews.models import Review
from django.db.models import Avg, Count, Q
from apps.users.services.add_user import create_user
from apps.users.services.update_user import update_user_data
from apps.users.services.delete_user import delete_user_data
from apps.users.validation.pydantic_schemas import RegisterSchema
from apps.reviews.services.spotify_service.spotify import search_albums
from apps.users.services.discover_user_service import search_users
from apps.reviews.services.review_service.discover_album_service import search_albums_and_artists
from apps.reviews.services.review_service.top_albums import get_album_avg_rating, get_trending_albums
from apps.reviews.services.review_service.profile_service import get_user_profile_data
from apps.users.services.follow_user import follow_service, unfollow_service
from apps.users.services.followers_service import get_followers_list, get_following_list
from apps.users.models import UserRelationship





def register_view(request):
    if request.method == "POST":
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'confirm_password': request.POST.get('confirm_password')
        }

        validated = RegisterSchema(**data)

        user = create_user(validated.username, validated.email, validated.password)

        if user.get('success'):
            messages.success(request, user.get('message'))
            return redirect('login')

        else: 
            messages.error(request, user.get('message'))
            return redirect('register')

    return render(request, 'users/auth/register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.filter(username=username).first()
            if not user:
                messages.error(request, "User does not exist")
                return redirect('login')

            if user.check_password(password):
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid password")
                return redirect('login')

        except Exception as e:
            messages.error(request, str(e))
            return redirect('login')

    return render(request, 'users/auth/login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('home')


@login_required
def account_view(request, username):
    if request.user.username != username:
        return redirect('account', username=request.user.username)

    user = request.user
    reviews = Review.objects.filter(user=user)
    reviews_count = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = 0.0

    # Get follower/following counts
    followers_count = UserRelationship.objects.filter(following=user).count()
    following_count = UserRelationship.objects.filter(user_id=user).count()

    if request.method == 'POST':
        if 'current_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect")
                return redirect('account', username=username)

            if new_password != confirm_password:
                messages.error(request, "New passwords do not match")
                return redirect('account', username=username)

            result = update_user_data(
                old_username=user.username,
                new_username=user.username,
                password=new_password
            )
            if result.get("success"):
                user.refresh_from_db()
                auth_login(request, user)
                messages.success(request, "Password updated successfully")
            else:
                messages.error(request, result.get("error", "Failed to update password"))
            return redirect('account', username=username)

        else:
            new_username = request.POST.get('username')
            new_email = request.POST.get('email')
            profile_picture = request.FILES.get('profile_picture')

            result = update_user_data(
                old_username=user.username,
                new_username=new_username,
                email=new_email,
                profile_picture=profile_picture
            )
            if result.get("success"):
                user.refresh_from_db()
                if new_username != username:
                    auth_login(request, user)
                messages.success(request, "Profile updated successfully")
                return redirect('account', username=new_username)
            else:
                messages.error(request, result.get("error", "Failed to update profile"))
                return redirect('account', username=username)

    return render(request, 'users/account.html', {
        'user': user,
        'reviews_count': reviews_count,
        'avg_rating': avg_rating,
        'followers_count': followers_count,
        'following_count': following_count,
    })


@login_required
@require_POST
def delete_account_view(request):
    result = delete_user_data(request.user.username)
    if result.get("success"):
        auth_logout(request)
        messages.success(request, "Account deleted successfully")
        return redirect('home')
    else:
        messages.error(request, result.get("message", "Failed to delete account"))
        return redirect('account', username=request.user.username)



@login_required
def discover_view(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    results = {
        'albums': [],
        'artists': [],
        'users': []
    }

    trending_albums = []

    if query:
        # Albums & Artists
        album_artist_results = search_albums_and_artists(
            query=query,
            search_type=search_type,
            search_albums_func=search_albums,
            get_album_avg_rating_func=get_album_avg_rating
        )
        results['albums'] = album_artist_results['albums']
        results['artists'] = album_artist_results['artists']

        # Users
        if search_type in ['all', 'users']:
            results['users'] = search_users(query)

    else:
        trending_albums = get_trending_albums(limit=8)

    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
        'trending_albums': trending_albums,
    }
    return render(request, 'reviews/discover.html', context)


@login_required
def delete_account_confirm_view(request):
    return render(request, 'users/delete_account_confirm.html')


@login_required
def user_profile(request, username):
    profile_data = get_user_profile_data(username)
    if not profile_data:
        messages.error(request, f"User '{username}' not found.")
        return redirect('home')

    # Check if current user is following this profile user
    is_following = False
    if request.user.is_authenticated and not request.user.username == username:
        try:
            profile_user = User.objects.get(username=username)
            is_following = UserRelationship.objects.filter(
                user_id=request.user,
                following=profile_user
            ).exists()
        except User.DoesNotExist:
            is_following = False

    # Get the actual user object for the template
    try:
        actual_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, f"User '{username}' not found.")
        return redirect('home')

    context = {
        'profile_user': actual_user,
        'user_reviews': profile_data.get('user_reviews', []),
        'review_count': profile_data.get('review_count', 0),
        'avg_rating': profile_data.get('avg_rating'),
        'is_own_profile': request.user.username == username,
        'is_following': is_following,
        'followers_count': profile_data.get('followers_count', 0),
        'following_count': profile_data.get('following_count', 0),
    }
    return render(request, 'reviews/user_profile.html', context)




@login_required
@require_POST
def follow_user(request, username):
    try:
        from apps.feed.services.notification_service import create_notification_service
        
        result = follow_service(request.user.id, username)
        
        # If follow was successful, create a notification
        if result["success"]:
            try:
                target_user = User.objects.get(username=username)
                
                # Fix: Pass the actual User object, not the ID
                create_notification_service(
                    recipient_id=target_user.id,  # Pass User object, not user_id
                    actor_id=request.user.id,     # Pass User object, not actor_id
                    notification_type='follow',
                    message=f'{request.user.username} started following you'
                )
                
                # Get updated follower count
                followers_count = UserRelationship.objects.filter(following=target_user).count()
                
            except User.DoesNotExist:
                print(f"Target user {username} not found for notification")
                followers_count = 0
            except Exception as e:
                print(f"Failed to create follow notification: {e}")
                followers_count = 0
        
        return JsonResponse({
            "success": result["success"],
            "message": result["message"],
            "following": result["success"],
            "followers_count": followers_count if result["success"] else 0
        })
    except Exception as e:
        print(f"Error in follow_user: {e}")
        return JsonResponse({
            "success": False,
            "message": str(e),
            "following": False,
            "followers_count": 0
        }, status=500)




@login_required
@require_POST
def unfollow_user(request, username):
    try:
        result = unfollow_service(request.user.id, username)
        
        return JsonResponse({
            "success": result["success"],
            "message": result["message"],
            "following": not result["success"]
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e),
            "following": True
        }, status=500)
    


@login_required
def followers_modal(request, username):
    """Modal endpoint for followers"""
    page = request.GET.get('page', 1)
    
    try:
        followers_data = get_followers_list(username, page, per_page=10)
        
        followers_html = []
        for follower in followers_data['followers']:
            # Check if current user is following this follower
            is_following_this_user = False
            if request.user.is_authenticated:
                try:
                    follower_user = User.objects.get(username=follower['username'])
                    is_following_this_user = UserRelationship.objects.filter(
                        user_id=request.user,
                        following=follower_user
                    ).exists()
                except User.DoesNotExist:
                    pass
            
            follow_button_html = ""
            if request.user.username != follower['username']:
                if is_following_this_user:
                    follow_button_html = f'''
                        <button class="follow-btn-modal px-4 py-2 bg-gray-500 text-white rounded-lg text-sm font-medium hover:bg-gray-600 transition-colors" 
                                data-username="{follower['username']}" data-following="true">
                            Following
                        </button>
                    '''
                else:
                    follow_button_html = f'''
                        <button class="follow-btn-modal px-4 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg text-sm font-medium hover:from-pink-600 hover:to-pink-700 transition-colors" 
                                data-username="{follower['username']}" data-following="false">
                            Follow
                        </button>
                    '''
            
            follower_html = f'''
                <div class="flex items-center justify-between p-6 hover:bg-gray-50 transition-colors">
                    <div class="flex items-center space-x-4">
                        <div class="w-14 h-14 rounded-full overflow-hidden bg-gray-200 flex-shrink-0">
                            <img src="{follower['profile_picture']}" class="w-full h-full object-cover" alt="{follower['username']}">
                        </div>
                        <div class="min-w-0 flex-1">
                            <h4 class="font-semibold text-gray-900 text-base truncate">{follower['username']}</h4>
                            <p class="text-sm text-gray-500 truncate">@{follower['username']}</p>
                        </div>
                    </div>
                    <div class="flex space-x-3 flex-shrink-0">
                        <a href="/users/profile/{follower['username']}/" class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                            View
                        </a>
                        {follow_button_html}
                    </div>
                </div>
            '''
            followers_html.append(follower_html)
        
        return JsonResponse({
            'success': True,
            'html': ''.join(followers_html),
            'has_more': followers_data['has_next'],
            'current_page': followers_data['current_page'],
            'total_count': followers_data['total_count']
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
def following_modal(request, username):
    """Modal endpoint for following"""
    page = request.GET.get('page', 1)
    
    try:
        # Debug: Check if user exists
        try:
            user = User.objects.get(username=username)
            print(f"Found user: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            print(f"User {username} not found")
            return JsonResponse({
                'success': False,
                'message': f'User {username} not found'
            }, status=404)
        
        # Debug: Check relationships directly
        relationships = UserRelationship.objects.filter(user_id=user)
        print(f"Found {relationships.count()} following relationships for {username}")
        for rel in relationships:
            print(f"  -> {user.username} is following {rel.following.username}")
        
        following_data = get_following_list(username, page, per_page=10)
        print(f"Following data returned: {following_data}")
        
        following_html = []
        for followed_user in following_data['following']:
            print(f"Processing followed user: {followed_user}")
            
            # Check if current user is following this user
            is_following_this_user = False
            if request.user.is_authenticated:
                try:
                    user_obj = User.objects.get(username=followed_user['username'])
                    is_following_this_user = UserRelationship.objects.filter(
                        user_id=request.user,
                        following=user_obj
                    ).exists()
                except User.DoesNotExist:
                    pass
            
            follow_button_html = ""
            if request.user.username != followed_user['username']:
                if is_following_this_user:
                    follow_button_html = f'''
                        <button class="follow-btn-modal px-4 py-2 bg-gray-500 text-white rounded-lg text-sm font-medium hover:bg-gray-600 transition-colors" 
                                data-username="{followed_user['username']}" data-following="true">
                            Following
                        </button>
                    '''
                else:
                    follow_button_html = f'''
                        <button class="follow-btn-modal px-4 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg text-sm font-medium hover:from-pink-600 hover:to-pink-700 transition-colors" 
                                data-username="{followed_user['username']}" data-following="false">
                            Follow
                        </button>
                    '''
            
            user_html = f'''
                <div class="flex items-center justify-between p-6 hover:bg-gray-50 transition-colors">
                    <div class="flex items-center space-x-4">
                        <div class="w-14 h-14 rounded-full overflow-hidden bg-gray-200 flex-shrink-0">
                            <img src="{followed_user['profile_picture']}" class="w-full h-full object-cover" alt="{followed_user['username']}">
                        </div>
                        <div class="min-w-0 flex-1">
                            <h4 class="font-semibold text-gray-900 text-base truncate">{followed_user['username']}</h4>
                            <p class="text-sm text-gray-500 truncate">@{followed_user['username']}</p>
                        </div>
                    </div>
                    <div class="flex space-x-3 flex-shrink-0">
                        <a href="/users/profile/{followed_user['username']}/" class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                            View
                        </a>
                        {follow_button_html}
                    </div>
                </div>
            '''
            following_html.append(user_html)
        
        result = {
            'success': True,
            'html': ''.join(following_html),
            'has_more': following_data['has_next'],
            'current_page': following_data['current_page'],
            'total_count': following_data['total_count']
        }
        print(f"Returning result: {result}")
        return JsonResponse(result)
        
    except Exception as e:
        print(f"Error in following_modal: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)