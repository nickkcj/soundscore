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
    """
    Handles user registration.
    On POST, validates form data, creates a new user, and redirects.
    On GET, renders the registration form.
    Parameters:
        request (HttpRequest): The incoming request object.
    Returns:
        HttpResponse: Renders the registration page or redirects on success/failure.
    """
    if request.method == "POST":
        # Collect data from the registration form
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'confirm_password': request.POST.get('confirm_password')
        }
        # Validate data using Pydantic schema
        validated = RegisterSchema(**data)
        # Call the service to create the user
        user = create_user(validated.username, validated.email, validated.password)

        if user.get('success'):
            # On success, show a message and redirect to the login page
            messages.success(request, user.get('message'))
            return redirect('login')
        else: 
            # On failure, show an error and redirect back to the registration page
            messages.error(request, user.get('message'))
            return redirect('register')
    # For GET requests, just show the registration form
    return render(request, 'users/auth/register.html')


def login_view(request):
    """
    Handles user login.
    On POST, authenticates the user and logs them in.
    On GET, renders the login form.
    Parameters:
        request (HttpRequest): The incoming request object.
    Returns:
        HttpResponse: Renders the login page or redirects on success/failure.
    """
    if request.method == "POST":
        # Collect username and password from the login form
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Find the user by username
            user = User.objects.filter(username=username).first()
            if not user:
                messages.error(request, "User does not exist")
                return redirect('login')
            # Check if the provided password is correct
            if user.check_password(password):
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid password")
                return redirect('login')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('login')
    # For GET requests, show the login form
    return render(request, 'users/auth/login.html')


def logout_view(request):
    """
    Logs the current user out.
    Parameters:
        request (HttpRequest): The incoming request object.
    Returns:
        HttpResponse: Redirects to the home page.
    """
    # Log the user out and redirect to the home page
    auth_logout(request)
    return redirect('home')


@login_required
def account_view(request, username):
    """
    Manages user account settings (profile info, password).
    Only allows users to view their own account page.
    Parameters:
        request (HttpRequest): The incoming request object.
        username (str): The username for the account page.
    Returns:
        HttpResponse: Renders the account page with user data.
    """
    # Ensure the user is viewing their own account page
    if request.user.username != username:
        return redirect('account', username=request.user.username)

    user = request.user
    # Get user stats: review count, average rating
    reviews = Review.objects.filter(user=user)
    reviews_count = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0.0
    # Get follower/following counts
    followers_count = UserRelationship.objects.filter(following=user).count()
    following_count = UserRelationship.objects.filter(user_id=user).count()

    if request.method == 'POST':
        # Check if the form submitted is for changing the password
        if 'current_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            # Validate passwords
            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect")
                return redirect('account', username=username)
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match")
                return redirect('account', username=username)
            # Update the password using the service
            result = update_user_data(old_username=user.username, new_username=user.username, password=new_password)
            if result.get("success"):
                user.refresh_from_db()
                auth_login(request, user) # Re-login user to maintain session
                messages.success(request, "Password updated successfully")
            else:
                messages.error(request, result.get("error", "Failed to update password"))
            return redirect('account', username=username)
        else:
            # Handle profile information update
            new_username = request.POST.get('username')
            new_email = request.POST.get('email')
            profile_picture = request.FILES.get('profile_picture')
            # Update profile data using the service
            result = update_user_data(old_username=user.username, new_username=new_username, email=new_email, profile_picture=profile_picture)
            if result.get("success"):
                user.refresh_from_db()
                if new_username != username:
                    auth_login(request, user) # Re-login if username changes
                messages.success(request, "Profile updated successfully")
                return redirect('account', username=new_username)
            else:
                messages.error(request, result.get("error", "Failed to update profile"))
                return redirect('account', username=username)
    # For GET requests, render the account page with current user data
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
    """
    Handles the final deletion of a user account.
    This is a POST-only view for security.
    Parameters:
        request (HttpRequest): The incoming request object.
    Returns:
        HttpResponse: Redirects to home on success or account page on failure.
    """
    # Call the service to delete the user's data
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
    """
    Renders the discover page for searching albums, artists, and users.
    If no query is provided, it shows trending albums.
    Parameters:
        request (HttpRequest): The incoming request object.
    Returns:
        HttpResponse: Renders the discover page with search results or trending data.
    """
    # Get search query and type from URL parameters
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    results = {'albums': [], 'artists': [], 'users': []}
    trending_albums = []

    if query:
        # If a search query is present, perform searches
        album_artist_results = search_albums_and_artists(query=query, search_type=search_type, search_albums_func=search_albums, get_album_avg_rating_func=get_album_avg_rating)
        results['albums'] = album_artist_results['albums']
        results['artists'] = album_artist_results['artists']
        if search_type in ['all', 'users']:
            results['users'] = search_users(query)
    else:
        # If no query, get trending albums to display
        trending_albums = get_trending_albums(limit=8)
    # Pass all data to the template
    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
        'trending_albums': trending_albums,
    }
    return render(request, 'reviews/discover.html', context)


@login_required
def delete_account_confirm_view(request):
    """
    Renders the confirmation page before deleting an account.
    Parameters:
        request (HttpRequest): The incoming request object.
    Returns:
        HttpResponse: Renders the delete confirmation page.
    """
    return render(request, 'users/delete_account_confirm.html')


@login_required
def user_profile(request, username):
    """
    Renders a user's profile page with their reviews, stats, and follow state.
    Parameters:
        request (HttpRequest): The incoming request object.
        username (str): The username of the profile to display.
    Returns:
        HttpResponse: Renders the user profile page.
    """
    # Get all profile data from the service
    profile_data = get_user_profile_data(username)
    if not profile_data:
        messages.error(request, f"User '{username}' not found.")
        return redirect('home')
    # Check if the logged-in user is following the profile user
    is_following = False
    if request.user.is_authenticated and not request.user.username == username:
        try:
            profile_user = User.objects.get(username=username)
            is_following = UserRelationship.objects.filter(user_id=request.user, following=profile_user).exists()
        except User.DoesNotExist:
            is_following = False
    # Get the actual user object for the template
    try:
        actual_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, f"User '{username}' not found.")
        return redirect('home')
    # Prepare context for the template
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
    """
    AJAX endpoint to follow a user.
    Creates a notification on success.
    Parameters:
        request (HttpRequest): The incoming request object.
        username (str): The username of the user to follow.
    Returns:
        JsonResponse: Success status, message, and updated follower count.
    """
    try:
        from apps.feed.services.notification_service import create_notification_service
        # Call the service to create the follow relationship
        result = follow_service(request.user.id, username)
        # If follow was successful, create a notification
        if result["success"]:
            try:
                target_user = User.objects.get(username=username)
                # Create a notification for the user who was followed
                create_notification_service(recipient_id=target_user.id, actor_id=request.user.id, notification_type='follow', message=f'{request.user.username} started following you')
                # Get the updated follower count to return to the frontend
                followers_count = UserRelationship.objects.filter(following=target_user).count()
            except User.DoesNotExist:
                followers_count = 0
            except Exception as e:
                followers_count = 0
        # Return JSON response for the frontend to handle
        return JsonResponse({"success": result["success"], "message": result["message"], "following": result["success"], "followers_count": followers_count if result["success"] else 0})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e), "following": False, "followers_count": 0}, status=500)


@login_required
@require_POST
def unfollow_user(request, username):
    """
    AJAX endpoint to unfollow a user.
    Parameters:
        request (HttpRequest): The incoming request object.
        username (str): The username of the user to unfollow.
    Returns:
        JsonResponse: Success status and message.
    """
    try:
        # Call the service to remove the follow relationship
        result = unfollow_service(request.user.id, username)
        # Return JSON response for the frontend
        return JsonResponse({"success": result["success"], "message": result["message"], "following": not result["success"]})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e), "following": True}, status=500)


@login_required
def followers_modal(request, username):
    """
    AJAX endpoint for the followers modal.
    Returns a paginated list of followers as HTML.
    Parameters:
        request (HttpRequest): The incoming request object.
        username (str): The username whose followers are being requested.
    Returns:
        JsonResponse: Contains the rendered HTML for the followers list.
    """
    page = request.GET.get('page', 1)
    try:
        # Get paginated list of followers from the service
        followers_data = get_followers_list(username, page, per_page=10)
        followers_html = []
        for follower in followers_data['followers']:
            # For each follower, check if the current user is following them back
            is_following_this_user = False
            if request.user.is_authenticated:
                try:
                    follower_user = User.objects.get(username=follower['username'])
                    is_following_this_user = UserRelationship.objects.filter(user_id=request.user, following=follower_user).exists()
                except User.DoesNotExist:
                    pass
            # Generate the correct follow/following button
            follow_button_html = ""
            if request.user.username != follower['username']:
                if is_following_this_user:
                    follow_button_html = f'''<button class="follow-btn-modal px-4 py-2 bg-gray-500 text-white rounded-lg text-sm font-medium hover:bg-gray-600 transition-colors" data-username="{follower['username']}" data-following="true">Following</button>'''
                else:
                    follow_button_html = f'''<button class="follow-btn-modal px-4 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg text-sm font-medium hover:from-pink-600 hover:to-pink-700 transition-colors" data-username="{follower['username']}" data-following="false">Follow</button>'''
            # Build the HTML for the follower entry
            follower_html = f'''<div class="flex items-center justify-between p-6 hover:bg-gray-50 transition-colors"><div class="flex items-center space-x-4"><div class="w-14 h-14 rounded-full overflow-hidden bg-gray-200 flex-shrink-0"><img src="{follower['profile_picture']}" class="w-full h-full object-cover" alt="{follower['username']}"></div><div class="min-w-0 flex-1"><h4 class="font-semibold text-gray-900 text-base truncate">{follower['username']}</h4><p class="text-sm text-gray-500 truncate">@{follower['username']}</p></div></div><div class="flex space-x-3 flex-shrink-0"><a href="/users/profile/{follower['username']}/" class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">View</a>{follow_button_html}</div></div>'''
            followers_html.append(follower_html)
        # Return the complete HTML and pagination info as JSON
        return JsonResponse({'success': True, 'html': ''.join(followers_html), 'has_more': followers_data['has_next'], 'current_page': followers_data['current_page'], 'total_count': followers_data['total_count']})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
def following_modal(request, username):
    """
    AJAX endpoint for the following modal.
    Returns a paginated list of users someone is following as HTML.
    Parameters:
        request (HttpRequest): The incoming request object.
        username (str): The username whose following list is being requested.
    Returns:
        JsonResponse: Contains the rendered HTML for the following list.
    """
    page = request.GET.get('page', 1)
    try:
        # Get paginated list of users being followed from the service
        following_data = get_following_list(username, page, per_page=10)
        following_html = []
        for followed_user in following_data['following']:
            # For each user, check if the current user is also following them
            is_following_this_user = False
            if request.user.is_authenticated:
                try:
                    user_obj = User.objects.get(username=followed_user['username'])
                    is_following_this_user = UserRelationship.objects.filter(user_id=request.user, following=user_obj).exists()
                except User.DoesNotExist:
                    pass
            # Generate the correct follow/following button
            follow_button_html = ""
            if request.user.username != followed_user['username']:
                if is_following_this_user:
                    follow_button_html = f'''<button class="follow-btn-modal px-4 py-2 bg-gray-500 text-white rounded-lg text-sm font-medium hover:bg-gray-600 transition-colors" data-username="{followed_user['username']}" data-following="true">Following</button>'''
                else:
                    follow_button_html = f'''<button class="follow-btn-modal px-4 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg text-sm font-medium hover:from-pink-600 hover:to-pink-700 transition-colors" data-username="{followed_user['username']}" data-following="false">Follow</button>'''
            # Build the HTML for the user entry
            user_html = f'''<div class="flex items-center justify-between p-6 hover:bg-gray-50 transition-colors"><div class="flex items-center space-x-4"><div class="w-14 h-14 rounded-full overflow-hidden bg-gray-200 flex-shrink-0"><img src="{followed_user['profile_picture']}" class="w-full h-full object-cover" alt="{followed_user['username']}"></div><div class="min-w-0 flex-1"><h4 class="font-semibold text-gray-900 text-base truncate">{followed_user['username']}</h4><p class="text-sm text-gray-500 truncate">@{followed_user['username']}</p></div></div><div class="flex space-x-3 flex-shrink-0"><a href="/users/profile/{followed_user['username']}/" class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">View</a>{follow_button_html}</div></div>'''
            following_html.append(user_html)
        # Return the complete HTML and pagination info as JSON
        result = {'success': True, 'html': ''.join(following_html), 'has_more': following_data['has_next'], 'current_page': following_data['current_page'], 'total_count': following_data['total_count']}
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)