from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from apps.users.models import User
from apps.users.services.auth.auth_service import register_user, authenticate_user


def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            register_user(username, email, password)

            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )
            user.save()

            messages.success(request, "User registered successfully")
            return redirect('login')

        except Exception as e:
            messages.error(request, str(e))
            return redirect('register')

    return render(request, 'auth/register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user_data = authenticate_user(username)

            user = User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create(
                    username=user_data['username'],
                    email=user_data.get('email', ''),
                    password=make_password(password)
                )

            if user.check_password(password):
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid password")
                return redirect('login')

        except Exception as e:
            messages.error(request, str(e))
            return redirect('login')

    return render(request, 'auth/login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('home')



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from apps.users.services.user_service import update_user, delete_user, get_user_profile_data


@login_required
def account_view(request, username):
    if request.user.username != username:
        return redirect('account', username=request.user.username)

    user = request.user

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

            update_user(username, password=new_password)
            user.set_password(new_password)
            user.save()
            auth_login(request, user)

            messages.success(request, "Password updated successfully")
            return redirect('account', username=username)

        else:
            new_username = request.POST.get('username')
            new_email = request.POST.get('email')
            profile_picture = request.FILES.get('profile_picture')

            update_user(username, new_username=new_username, email=new_email, profile_picture=profile_picture)

            user.username = new_username
            user.email = new_email
            if profile_picture:
                user.profile_picture = profile_picture
            user.save()

            if new_username != username:
                auth_login(request, user)

            messages.success(request, "Profile updated successfully")
            return redirect('account', username=new_username)

    profile_data = get_user_profile_data(username)

    return render(request, 'users/account.html', {
        'user': user,
        'reviews_count': profile_data['reviews_count'],
        'avg_rating': profile_data['avg_rating'],
        'profile_picture_url': profile_data['profile_picture_url']
    })


@login_required
def delete_account_view(request):
    delete_user(request.user.username)
    request.user.delete()
    auth_logout(request)
    return redirect('home')
