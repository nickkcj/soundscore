from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
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

    context = {
        'profile_user': profile_data['user'],
        'user_reviews': profile_data['user_reviews'],
        'review_count': profile_data['review_count'],
        'avg_rating': profile_data['avg_rating'],
        'is_own_profile': request.user.username == username,
    }
    return render(request, 'reviews/user_profile.html', context)
