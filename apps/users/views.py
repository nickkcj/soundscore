from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from apps.users.models import User
from apps.users.services.add_user import create_user
from apps.users.services.update_user import update_user_data
from apps.users.services.delete_user import delete_user_data


def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = create_user(username, email, password)

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
    })


@login_required
def delete_account_view(request):
    result = delete_user_data(request.user.username)
    if result.get("success"):
        auth_logout(request)
        messages.success(request, "Account deleted successfully")
        return redirect('home')
    else:
        messages.error(request, result.get("message", "Failed to delete account"))
        return redirect('account', username=request.user.username)


def discover_view(request):
    pass
