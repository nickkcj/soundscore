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
from .apis.spotify import search_albums # Assuming this returns a list of dicts
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from .services.review.add_review import add_review_supabase
from datetime import datetime
from .services.review.edit_review import edit_review_supabase
from .services.review.delete_review import delete_review_supabase
from .services.user.add_user import add_user_supabase
from .services.user.supabase_client import authenticate_with_jwt
from .services.user.delete_user import delete_user_data_supabase
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
            response = add_user_supabase(username, password, email)
            if "error" in response:
                messages.error(request, response["error"])
                return redirect('register')
            
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
            client = authenticate_with_jwt()
            user_supabase = client.table('soundscore_user').select('id').eq('username', username).limit(1).execute()
            if user_supabase:
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

    # Get Supabase client
    client = authenticate_with_jwt()
    if not client:
        messages.error(request, "Could not connect to Supabase.")
        return redirect('home')

    # Get Supabase user ID by username
    user_response = client.table('soundscore_user').select('id').eq('username', username).limit(1).execute()
    if not user_response.data:
        messages.error(request, f"User '{username}' not found in Supabase.")
        return redirect('home')
    supabase_user_id = user_response.data[0]['id']

    # Fetch all reviews for this user, including album info
    all_reviews_response = client.table('soundscore_review')\
        .select('*, soundscore_album(title, artist, cover_image, spotify_id)')\
        .eq('user_id', supabase_user_id)\
        .order('created_at', desc=True)\
        .execute()
    all_reviews = all_reviews_response.data or []

    for review in all_reviews:
        if 'created_at' not in review:
            review['created_at'] = datetime.now().isoformat()

    # Fetch favorite reviews
    favorite_reviews = [review for review in all_reviews if review.get('is_favorite')]

    # Calculate average rating
    if all_reviews:
        avg = sum(r['rating'] for r in all_reviews) / len(all_reviews)
        average_rating = f"{avg:.1f}"
    else:
        average_rating = "N/A"

    context = {
        'user': user,
        'all_reviews': all_reviews,
        'favorite_albums': favorite_reviews,
        'total_reviews': len(all_reviews),
        'average_rating': average_rating,
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
            print(f"[DEBUG] Validation failed: album_id={album_id}, rating={rating}")
            return JsonResponse({"error": "Album ID and rating are required"}, status=400)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({"error": "Rating must be between 1 and 5"}, status=400)
        except ValueError:
            return JsonResponse({"error": "Rating must be a number"}, status=400)
        
        # IMPORTANT: Look up the Supabase user ID by username instead of using Django's ID
        
        client = authenticate_with_jwt()
        if not client:
            return JsonResponse({"error": "Failed to authenticate with Supabase"}, status=500)
        
        # Get the username from Django's user object
        username = request.user.username
        
        # Query Supabase to get the user ID
        user_response = client.table('soundscore_user').select('id').eq('username', username).limit(1).execute()
        
        if not user_response.data:
            return JsonResponse({"error": f"User '{username}' not found in Supabase"}, status=404)
            
        supabase_user_id = user_response.data[0]['id']
        
        # Call the Supabase function with the CORRECT user ID
        result = add_review_supabase(
            user_id=supabase_user_id,  # Use the Supabase user ID
            album_id=album_id,
            rating=rating,
            album_title=album_title,
            album_artist=album_artist, 
            album_cover=album_cover,
            text=review_text,
            is_favorite=is_favorite
        )
        
        # Check if there was an error
        if "error" in result:
            return JsonResponse({"error": result["error"]}, status=400)
        
        # Return success response
        return JsonResponse({
            "success": True,
            "message": "Review saved successfully",
            "review_id": result.get("review", {}).get("id")
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
        


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
                 spotify_album_results = [] # Force to empty list if not a list and not an error dict

        except Exception as e:
            # Catch errors during the search_albums call itself
            messages.error(request, "An unexpected error occurred while searching Spotify.")
            spotify_album_results = [] # Ensure it's an empty list on critical failure
            spotify_album_results_cache = spotify_album_results


        # --- Process Albums (only if spotify_album_results is a list) ---
        if search_type in ['all', 'albums'] and isinstance(spotify_album_results, list):
            try:
                processed_albums = []
                # Use enumerate to get index for better debugging
                for i, album_data in enumerate(spotify_album_results):

                    # Check for essential keys before proceeding
                    album_id = album_data.get('id')
                    if not album_id:
                        continue

                    current_album = album_data.copy()

                    # Debug the helper function call
                    try:
                        avg_rating = get_album_avg_rating(album_id)
                    except Exception as helper_e:
                        avg_rating = None # Default to None if helper fails

                    current_album['avg_rating'] = avg_rating if avg_rating is not None else 'Not rated'
                    processed_albums.append(current_album)

                results['albums'] = processed_albums
            except KeyError as ke:
                 messages.error(request, f"Error processing album results due to missing data: {ke}")
            except Exception as e:
                messages.error(request, "Error processing album results.")

        # --- Process Artists (only if spotify_album_results is a list) ---
        if search_type in ['all', 'artists'] and isinstance(spotify_album_results, list):
            try:
                artists_dict = {}
                # Use enumerate for better debugging
                for i, album_data in enumerate(spotify_album_results):

                    # Check for essential keys
                    artist_name = album_data.get('artist')
                    album_id = album_data.get('id')

                    if not artist_name:
                        continue
                    if not album_id:
                        continue

                    current_album_for_artist = album_data.copy()

                    # Debug the helper function call
                    try:
                        avg_rating = get_album_avg_rating(album_id)
                    except Exception as helper_e:
                        avg_rating = None # Default to None if helper fails

                    current_album_for_artist['avg_rating'] = avg_rating if avg_rating is not None else 'Not rated'

                    if artist_name not in artists_dict:
                        artists_dict[artist_name] = {'name': artist_name, 'albums': []}

                    artists_dict[artist_name]['albums'].append(current_album_for_artist)

                results['artists'] = list(artists_dict.values())
            except KeyError as ke:
                 messages.error(request, f"Error processing artist results due to missing data: {ke}")
            except Exception as e:
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
                        results['users'] = user_list
            except Exception as e:
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
        'profile_user': profile_user,
        'user_reviews': user_reviews,
        'review_count': review_count,
        'avg_rating': round(avg_rating, 1) if avg_rating is not None else None,
        'is_own_profile': request.user == profile_user
    }
    return render(request, 'user_profile.html', context)


@login_required
def edit_review(request, review_id):
    # Get Supabase client
    client = authenticate_with_jwt()
    if not client:
        messages.error(request, "Could not connect to Supabase.")
        return redirect('home')
    
    # Get the Supabase user ID for the current user
    username = request.user.username
    user_response = client.table('soundscore_user').select('id').eq('username', username).limit(1).execute()
    
    if not user_response.data:
        messages.error(request, f"User '{username}' not found in Supabase.")
        return redirect('home')
    
    supabase_user_id = user_response.data[0]['id']
    
    # Get the review from Supabase
    review_response = client.table('soundscore_review')\
        .select('*, soundscore_album(title, artist, cover_image, spotify_id)')\
        .eq('id', review_id)\
        .limit(1)\
        .execute()
    
    if not review_response.data:
        messages.error(request, "Review not found.")
        return redirect('reviews', username=request.user.username)
    
    review = review_response.data[0]
    
    # Ensure the logged-in user is the owner of the review
    if review['user_id'] != supabase_user_id:
        return HttpResponseForbidden("You are not allowed to edit this review.")

    # Handle POST request - editing the review
    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating'))
            text = request.POST.get('review_text', '')
            is_favorite = 'is_favorite' in request.POST
            
            # Call the service function to update the review
            result = edit_review_supabase(
                review_id=review_id,
                rating=rating,
                text=text,
                is_favorite=is_favorite
            )
            
            if "error" in result:
                messages.error(request, result["error"])
            else:
                messages.success(request, "Review updated successfully!")
                
            return redirect('reviews', username=request.user.username)
            
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating value.")
        except Exception as e:
            messages.error(request, f"Error updating review: {str(e)}")
    
    # If GET request, display the form pre-filled with review data
    context = {
        'review': review,
        'album_data': review['soundscore_album'],
        'cover_image': review['soundscore_album'].get('cover_image'),
        'album_title': review['soundscore_album'].get('title'),
        'album_artist': review['soundscore_album'].get('artist')
    }
    return render(request, 'edit_review.html', context)



@login_required
@require_POST
def delete_review(request, review_id):
    delete = delete_review_supabase(request.user.username, review_id)
    if delete.get('error'):
        messages.error(request, delete['error'])
    else:
        messages.success(request, "Review deleted successfully!")

    return redirect('reviews', username=request.user.username)

@login_required
@require_POST # Ensure this view only accepts POST requests
def delete_account(request):
    print("REACHED HERE")
    user_to_delete = request.user # Get the currently logged-in user

    # Call the service function to delete user data from custom tables
    result = delete_user_data_supabase(user_to_delete.username)

    if result.get('error'):
        messages.error(request, result['error'])
        # Redirect back to account page if deletion fails
        return redirect('account', username=user_to_delete.username)
    elif result.get('warning'):
         messages.warning(request, result['warning'])
         # Log out even if only a warning occurred (e.g., user already partially deleted)
    else:
        messages.success(request, result.get('message', 'Account data deleted.'))

    # Log the user out from Django session
    auth_logout(request)

    # Add a final message after logout
    messages.info(request, "You have been logged out.")

    # Redirect to the home page after successful deletion and logout
    return redirect('home')


@login_required # Ensure user is logged in
def delete_account_confirm(request):
    return render(request, 'delete_account_confirm.html')