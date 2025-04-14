from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Album, Review # Make sure Album and Review are imported
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404 # Import Http404
import json
from django.db.models import Avg, Q # Import Q for complex lookups
from apis.spotify import search_albums # Assuming this returns a list of dicts

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
    
    # Fetch all reviews
    all_reviews = Review.objects.filter(user=user).order_by('-created_at')
    
    # Fetch favorite reviews
    favorite_albums = Review.objects.filter(user=user, is_favorite=True).select_related('album')
    
    # Calculate average rating
    average_rating = "N/A"
    if all_reviews.exists():
        avg = all_reviews.aggregate(Avg('rating'))['rating__avg']
        average_rating = f"{avg:.1f}"
    
    context = {
        'user': user,
        'all_reviews': all_reviews,
        'favorite_albums': favorite_albums,
        'total_reviews': all_reviews.count(),
        'average_rating': average_rating
    }
    return render(request, 'reviews.html', context)

@login_required
def create_review(request, username):
    search_results = []
    query = None

    if request.method == 'POST':
        query = request.POST.get('artist_name', '').strip()
        if query:
            search_results = search_albums(query)

    context = {
        'search_results': search_results,
        'query': query,
    }
    return render(request, 'create_review.html', context)

# This is your existing search API endpoint
def search_albums_api_view(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({"error": "Search query is required"}, status=400)
    
    albums = search_albums(query)
    return JsonResponse({"albums": albums})

# Add this new function to handle review creation
@login_required
def create_review_api(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        album_id = data.get('album_id')
        album_title = data.get('album_title')
        album_artist = data.get('album_artist')
        album_cover = data.get('album_cover')
        rating = data.get('rating')
        review_text = data.get('review_text', '')
        is_favorite = data.get('is_favorite', False)
        
        # Basic validation
        if not album_id or not rating:
            return JsonResponse({"error": "Album ID and rating are required"}, status=400)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({"error": "Rating must be between 1 and 5"}, status=400)
        except ValueError:
            return JsonResponse({"error": "Rating must be a number"}, status=400)
        
        # Get or create the album
        album, created = Album.objects.get_or_create(
            spotify_id=album_id,
            defaults={
                'title': album_title,
                'artist': album_artist,
                'cover_image': album_cover
            }
        )
        
        # Create or update the review
        review, created = Review.objects.update_or_create(
            user=request.user,
            album=album,
            defaults={
                'rating': rating,
                'text': review_text,
                'is_favorite': is_favorite
            }
        )
        
        return JsonResponse({
            "success": True,
            "message": "Review saved successfully",
            "review_id": review.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Helper function to get average rating for an album (optional, but cleans up the view)
def get_album_avg_rating(spotify_id):
    try:
        db_album = Album.objects.filter(spotify_id=spotify_id).first()
        if db_album:
            avg_rating = Review.objects.filter(album=db_album).aggregate(Avg('rating'))['rating__avg']
            return round(avg_rating, 1) if avg_rating is not None else None
    except Album.DoesNotExist:
        pass
    return None

@login_required
def discover(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    results = {
        'albums': [],
        'artists': [],
        'users': []
    }
    spotify_album_results_cache = None # Cache Spotify results

    if query:
        # --- Attempt to fetch from Spotify ---
        try:
            # Call the API function (ensure this is from .apis.spotify)
            spotify_album_results = search_albums(query)
            spotify_album_results_cache = spotify_album_results # Cache for potential artist search

            # --- Check if Spotify returned an error ---
            if isinstance(spotify_album_results, dict) and 'error' in spotify_album_results:
                # Display the error from the API function
                messages.error(request, f"Spotify Error: {spotify_album_results['error']}")
                # Keep results empty, the error message will show
                spotify_album_results = [] # Ensure it's an empty list for subsequent checks

            # --- Ensure we have a list before proceeding ---
            if not isinstance(spotify_album_results, list):
                 print(f"Warning: Expected list from search_albums, got {type(spotify_album_results)}. Treating as empty.")
                 spotify_album_results = [] # Force to empty list if not a list and not an error dict

        except Exception as e:
            # Catch errors during the search_albums call itself
            print(f"Critical Error calling search_albums: {str(e)}")
            messages.error(request, "An unexpected error occurred while searching Spotify.")
            spotify_album_results = [] # Ensure it's an empty list on critical failure
            spotify_album_results_cache = spotify_album_results


        # --- Process Albums (only if spotify_album_results is a list) ---
        if search_type in ['all', 'albums'] and isinstance(spotify_album_results, list):
            print(f"DEBUG: Processing {len(spotify_album_results)} albums for 'Albums' section...") # <-- Add
            try:
                processed_albums = []
                # Use enumerate to get index for better debugging
                for i, album_data in enumerate(spotify_album_results):
                    print(f"DEBUG [Album {i}]: Processing album data: {album_data.get('title')} (ID: {album_data.get('id')})") # <-- Add

                    # Check for essential keys before proceeding
                    album_id = album_data.get('id')
                    if not album_id:
                        print(f"DEBUG [Album {i}]: Skipping album due to missing 'id'.") # <-- Add
                        continue

                    current_album = album_data.copy()

                    # Debug the helper function call
                    try:
                        print(f"DEBUG [Album {i}]: Calling get_album_avg_rating with ID: {album_id}") # <-- Add
                        avg_rating = get_album_avg_rating(album_id)
                        print(f"DEBUG [Album {i}]: Result from get_album_avg_rating: {avg_rating}") # <-- Add
                    except Exception as helper_e:
                        print(f"ERROR [Album {i}]: Error inside get_album_avg_rating for ID {album_id}: {helper_e}") # <-- Add specific error
                        avg_rating = None # Default to None if helper fails

                    current_album['avg_rating'] = avg_rating if avg_rating is not None else 'Not rated'
                    processed_albums.append(current_album)

                results['albums'] = processed_albums
                print(f"DEBUG: Finished processing albums. Added {len(processed_albums)} albums to results.") # <-- Add
            except KeyError as ke:
                 print(f"ERROR during album processing loop (KeyError): Missing key {ke} in album data: {album_data}") # <-- Specific error
                 messages.error(request, f"Error processing album results due to missing data: {ke}")
            except Exception as e:
                print(f"ERROR during album processing loop (General): {str(e)}") # <-- Modify existing
                messages.error(request, "Error processing album results.")

        # --- Process Artists (only if spotify_album_results is a list) ---
        if search_type in ['all', 'artists'] and isinstance(spotify_album_results, list):
            print(f"DEBUG: Processing {len(spotify_album_results)} albums for 'Artists' section...") # <-- Add
            try:
                artists_dict = {}
                # Use enumerate for better debugging
                for i, album_data in enumerate(spotify_album_results):
                    print(f"DEBUG [Artist Album {i}]: Processing album data for artist grouping: {album_data.get('title')}") # <-- Add

                    # Check for essential keys
                    artist_name = album_data.get('artist')
                    album_id = album_data.get('id')

                    if not artist_name:
                        print(f"DEBUG [Artist Album {i}]: Skipping album due to missing 'artist'.") # <-- Add
                        continue
                    if not album_id:
                        print(f"DEBUG [Artist Album {i}]: Skipping album due to missing 'id'.") # <-- Add
                        continue

                    current_album_for_artist = album_data.copy()

                    # Debug the helper function call
                    try:
                        print(f"DEBUG [Artist Album {i}]: Calling get_album_avg_rating with ID: {album_id}") # <-- Add
                        avg_rating = get_album_avg_rating(album_id)
                        print(f"DEBUG [Artist Album {i}]: Result from get_album_avg_rating: {avg_rating}") # <-- Add
                    except Exception as helper_e:
                        print(f"ERROR [Artist Album {i}]: Error inside get_album_avg_rating for ID {album_id}: {helper_e}") # <-- Add specific error
                        avg_rating = None # Default to None if helper fails

                    current_album_for_artist['avg_rating'] = avg_rating if avg_rating is not None else 'Not rated'

                    if artist_name not in artists_dict:
                        artists_dict[artist_name] = {'name': artist_name, 'albums': []}

                    artists_dict[artist_name]['albums'].append(current_album_for_artist)

                results['artists'] = list(artists_dict.values())
                print(f"DEBUG: Finished processing artists. Found {len(results['artists'])} artists.") # <-- Add
            except KeyError as ke:
                 print(f"ERROR during artist processing loop (KeyError): Missing key {ke} in album data: {album_data}") # <-- Specific error
                 messages.error(request, f"Error processing artist results due to missing data: {ke}")
            except Exception as e:
                print(f"ERROR during artist processing loop (General): {str(e)}") # <-- Modify existing
                messages.error(request, "Error processing artist results.")

        # --- Search Users ---
        # (User search logic remains the same as it was working)
        if search_type in ['all', 'users']:
            try:
                user_queryset = User.objects.filter(username__icontains=query).only(
                    'username', 'profile_picture'
                )[:10]
                user_list = []
                for user in user_queryset:
                    try:
                        user_reviews = Review.objects.filter(user=user)
                        review_count = user_reviews.count()
                        avg_rating_data = user_reviews.aggregate(Avg('rating'))
                        avg_rating = avg_rating_data.get('rating__avg')
                        user_list.append({
                            'username': user.username,
                            'profile_picture_url': user.profile_picture.url if user.profile_picture else None,
                            'review_count': review_count,
                            'avg_rating': round(avg_rating, 1) if avg_rating is not None else 'No ratings'
                        })
                    except Exception as e_user:
                        print(f"Error processing user {user.username}: {str(e_user)}")
                results['users'] = user_list
            except Exception as e:
                print(f"Error searching users: {str(e)}")
                messages.error(request, "Could not fetch user results.")

    context = {
        'query': query,
        'search_type': search_type,
        'results': results
    }
    return render(request, 'discover.html', context)


# Ensure you have the user_profile view (even if it redirects for now)
@login_required
def user_profile(request, username):
    # Get the user object for the requested username, or return 404 if not found
    profile_user = get_object_or_404(User, username=username)
    
    # Get reviews by this user, ordered by creation date (newest first)
    user_reviews = Review.objects.filter(user=profile_user).order_by('-created_at')
    
    # Calculate review statistics
    review_count = user_reviews.count()
    avg_rating_data = user_reviews.aggregate(Avg('rating'))
    avg_rating = avg_rating_data.get('rating__avg')

    context = {
        'profile_user': profile_user, # The user whose profile is being viewed
        'user_reviews': user_reviews,
        'review_count': review_count,
        'avg_rating': round(avg_rating, 1) if avg_rating is not None else None,
        'is_own_profile': request.user == profile_user # Flag to check if it's the logged-in user's profile
    }
    return render(request, 'user_profile.html', context)
