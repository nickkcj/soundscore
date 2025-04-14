from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import User
from django.contrib import messages
from django.contrib.auth import logout as auth_logout # Rename import to avoid conflict
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

#Whenever using a variable use double curly braces

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        print(username, email, password, confirm_password)

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')
        
        try:
            password = make_password(password) 
            user = User.objects.create(username=username, email=email, password=password)
            user.save()
            auth_logout(request)
            messages.success(request, "User registered successfully!")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('register')
        
    return render(request, 'register.html')


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Print for debugging
        print(f"Login attempt for username: {username}")

        try:
            # First check if user exists
            user = User.objects.get(username=username)
            
            # Then verify password - use Django's built-in check_password
            if user.check_password(password):
                # Log the user in
                auth_login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')
            else:
                # Password doesn't match
                messages.error(request, "Invalid password")
                return redirect('login')
                
        except User.DoesNotExist:
            # User doesn't exist
            messages.error(request, "User does not exist")
            return redirect('login')
        except Exception as e:
            # Catch any other errors
            print(f"Login error: {e}")
            messages.error(request, f"Error during login: {str(e)}")
            return redirect('login')
            
    # GET request - show login form
    return render(request, 'login.html')

# Remove the old account_update view

@login_required
def account(request, username):
    # Ensure users can only access/edit their own account page via this view
    # You might want to fetch the specific user if you allow viewing others' profiles,
    # but for editing, always use request.user
    if request.user.username != username:
        # Redirect to the logged-in user's own account page if they try to access someone else's
        return redirect('account', username=request.user.username)

    user = request.user # Use the logged-in user for context and updates

    if request.method == 'POST':
        # --- Handle the form submission (Update Logic) ---
        user.email = request.POST.get('email', user.email)

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            # Optional: Delete old picture before saving new one
            # if user.profile_picture and user.profile_picture.name != 'profile_pics/default.jpg':
            #     user.profile_picture.delete(save=False)
            user.profile_picture = request.FILES['profile_picture']

        # Handle password update (only if a new password was entered)
        password = request.POST.get('password')
        if password:
            # Add validation: check current password before allowing change (more secure)
            # For simplicity here, we just set the new password if provided
            user.set_password(password) # Hashes the password

        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            # Redirect back to the SAME account page after saving to prevent re-posting
            return redirect('account', username=user.username)
        except Exception as e:
            messages.error(request, f'Error updating profile: {e}')
            # If error, fall through to render the page again (showing the error message)

    # --- Handle the initial page load (GET Request) ---
    context = {'user': user} # Pass the user object to the template
    return render(request, 'account.html', context)

# Add the logout view
def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home') # Redirect to home page after logout


def reviews(request, username):
    user = get_object_or_404(User, username=username)
    # Fetch reviews related to the user if you have a Review model
    # reviews = Review.objects.filter(user=user)
    context = {
        'user': user,
        # 'reviews': reviews,  # Uncomment if you have a Review model
    }
    return render(request, 'reviews.html', context)

@login_required
def create_review(request, username):
    return render(request, 'create_review.html')
