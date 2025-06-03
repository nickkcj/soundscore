from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ..models import User
from ..services.user.supabase_client import authenticate_with_jwt
from ..services.user.add_user import add_user_supabase
from ..services.user.update_user import update_user_supabase
from ..services.user.delete_user import delete_user_data_supabase
from ..validation.pydantic_schemas import RegisterSchema
from pydantic import ValidationError

def register(request):
    if request.method == "POST":
        data = {
            "username": request.POST.get('username'),
            "email": request.POST.get('email'),
            "password": request.POST.get('password'),
            "confirm_password": request.POST.get('confirm_password')
        }

        try:
            # Validation with Pydantic
            validated = RegisterSchema(**data)

            # Check if username or email already exists
            if User.objects.filter(username=validated.username).exists():
                messages.error(request, "Username already exists")
                return redirect('register')
            if User.objects.filter(email=validated.email).exists():
                messages.error(request, "Email already exists")
                return redirect('register')

            # Create in Supabase
            response = add_user_supabase(validated.username, validated.password, validated.email)
            if "error" in response:
                messages.error(request, response["error"])
                return redirect('register')

            # Create locally
            user = User.objects.create(
                username=validated.username,
                email=validated.email,
                password=make_password(validated.password)
            )
            user.save()

            auth_logout(request)
            messages.success(request, "User registered successfully!")
            return redirect('login')

        except ValidationError as e:
            for error in e.errors():
                msg = error['msg']
                if msg.lower().startswith("value error, "):
                    msg = msg[13:]
            messages.error(request, msg)  
            return redirect('register')

        except Exception as e:
            # Show only the error message, not technical details
            messages.error(request, str(e))
            return redirect('register')

    return render(request, 'auth/register.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Login attempt for username: {username}")

        try:
            # Attempt to fetch from Supabase only once
            client = authenticate_with_jwt()
            response = client.table('soundscore_user') \
                .select('id,username,email') \
                .eq('username', username) \
                .limit(1) \
                .execute()
            
            user_data = response.data[0] if response.data else None
            print(user_data)
            if not user_data:
                messages.error(request, "User does not exist")
                return redirect('login')

            # Check local DB first (avoid hitting DB if already exists)
            user = User.objects.filter(username=username).first()
            if not user:
                print(f"User {username} found in Supabase but not locally - creating local record")
                user = User.objects.create(
                    username=user_data['username'],
                    email=user_data.get('email', ''),
                    password=make_password(password)  # temp until verification
                )

            # Password check (local)
            if user.check_password(password):
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid password")
                return redirect('login')

        except Exception as e:
            print(f"Login error: {e}")
            messages.error(request, str(e))
            return redirect('login')

    return render(request, 'auth/login.html')


@login_required
def account(request, username):
    if request.user.username != username:
        # Redirect to the logged-in user's own account page if they try to access someone else's
        return redirect('account', username=request.user.username)

    user = request.user # Use the logged-in user for context and updates

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_email = request.POST.get('email', user.email)
        new_password = request.POST.get('password')
        profile_pic = request.FILES.get('profile_picture')
        
        # First update in Supabase
        result = update_user_supabase(
            old_username=username,
            new_username=new_username if new_username != user.username else user.username,
            email=new_email if new_email != user.email else None,
            password=new_password if new_password else None,
            profile_picture=profile_pic
        )
        
        if result.get('error'):
            messages.error(request, result['error'])
            return render(request, 'users/account.html', {'user': user})
            
        # Then update the Django user
        user.username = new_username
        user.email = new_email
        
        if profile_pic:
            user.profile_picture = profile_pic
            
        if new_password:
            user.set_password(new_password)
            
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            
            # If password or username changed, re-login user to prevent logout
            if new_password or new_username != username:
                auth_login(request, user)
                
            # Use new username for redirect
            return redirect('account', username=new_username)
        except Exception as e:
            messages.error(request, str(e))

    # Get the user's profile picture URL from Supabase
    client = authenticate_with_jwt()
    if client:
        try:
            user_response = client.table('soundscore_user') \
                .select('profile_picture') \
                .eq('username', username) \
                .limit(1) \
                .execute()
                
            if user_response.data and user_response.data[0].get('profile_picture'):
                user.profile_picture_url = user_response.data[0]['profile_picture']
        except Exception as e:
            print(f"Error fetching profile picture from Supabase: {e}")

    # --- Handle the initial page load (GET Request) ---
    context = {'user': user}
    return render(request, 'users/account.html', context)

def logout_view(request):
    auth_logout(request)
    return redirect('home')

@login_required
@require_POST
def delete_account(request):
    user_to_delete = request.user

    # Call the service function to delete user data from custom tables
    result = delete_user_data_supabase(user_to_delete.username)

    if result.get('error'):
        messages.error(request, result['error'])
        # Redirect back to account page if deletion fails
        return redirect('account', username=user_to_delete.username)

    # Log the user out from Django session
    auth_logout(request)

    # Redirect to the home page after successful deletion and logout
    return redirect('home')

@login_required
def delete_account_confirm(request):
    return render(request, 'users/delete_account_confirm.html')
