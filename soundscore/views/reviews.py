from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Avg
from datetime import datetime
import json
from ..models import User, Album, Review
from ..services.spotify import search_albums
from ..services.review.add_review import add_review_supabase
from ..services.review.edit_review import edit_review_supabase
from ..services.review.delete_review import delete_review_supabase
from ..services.user.supabase_client import authenticate_with_jwt, get_admin_client
from ..services.comment.comment_service import get_comments_for_review  # You'll create this
from django.views.decorators.cache import cache_page

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
    return render(request, 'reviews/create_review.html', context)

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

def reviews(request, username):
    user = get_object_or_404(User, username=username)

    # Get Supabase client
    client = authenticate_with_jwt()
    if not client:
        messages.error(request, "Could not connect to Supabase.")
        return redirect('home')

    # Get Supabase user ID by username - ADD profile_picture to select
    user_response = client.table('soundscore_user').select('id, profile_picture').eq('username', username).limit(1).execute()
    if not user_response.data:
        messages.error(request, f"User '{username}' not found in Supabase.")
        return redirect('home')
    supabase_user_id = user_response.data[0]['id']
    
    # Add profile picture URL to user object
    if user_response.data[0].get('profile_picture'):
        user.profile_picture_url = user_response.data[0]['profile_picture']

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
    return render(request, 'reviews/reviews.html', context)

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
        return redirect('reviews.reviews', username=request.user.username)
    
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
    return render(request, 'reviews/edit_review.html', context)

@login_required
@require_POST
def delete_review(request, review_id):
    delete = delete_review_supabase(request.user.username, review_id)
    if delete.get('error'):
        messages.error(request, delete['error'])
    else:
        messages.success(request, "Review deleted successfully!")

    return redirect('reviews', username=request.user.username)

def search_albums_api_view(request):
    query = request.GET.get('q', '')
    if not query:
         return JsonResponse({"error": "Search query is required"}, status=400)
    
    albums = search_albums(query)
    return JsonResponse({"albums": albums})

@login_required
def discover(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    results = {
        'albums': [],
        'artists': [],
        'users': []
    }
    spotify_album_results_cache = None

    # --- Spotify album/artist search remains unchanged ---
    if query:
        try:
            spotify_album_results = search_albums(query)
            spotify_album_results_cache = spotify_album_results
            if isinstance(spotify_album_results, dict) and 'error' in spotify_album_results:
                messages.error(request, f"Spotify Error: {spotify_album_results['error']}")
                spotify_album_results = []
            if not isinstance(spotify_album_results, list):
                spotify_album_results = []
        except Exception as e:
            messages.error(request, "An unexpected error occurred while searching Spotify.")
            spotify_album_results = []
            spotify_album_results_cache = spotify_album_results

        # --- Process Albums (unchanged) ---
        if search_type in ['all', 'albums'] and isinstance(spotify_album_results, list):
            try:
                processed_albums = []
                for i, album_data in enumerate(spotify_album_results):
                    album_id = album_data.get('id')
                    if not album_id:
                        continue
                    current_album = album_data.copy()
                    try:
                        avg_rating = get_album_avg_rating(album_id)
                    except Exception as helper_e:
                        avg_rating = None
                    current_album['avg_rating'] = avg_rating if avg_rating is not None else 'Not rated'
                    processed_albums.append(current_album)
                results['albums'] = processed_albums
            except KeyError as ke:
                messages.error(request, f"Error processing album results due to missing data: {ke}")
            except Exception as e:
                messages.error(request, "Error processing album results.")

        # --- Process Artists (unchanged) ---
        if search_type in ['all', 'artists'] and isinstance(spotify_album_results, list):
            try:
                artists_dict = {}
                for i, album_data in enumerate(spotify_album_results):
                    artist_name = album_data.get('artist')
                    album_id = album_data.get('id')
                    if not artist_name or not album_id:
                        continue
                    current_album_for_artist = album_data.copy()
                    try:
                        avg_rating = get_album_avg_rating(album_id)
                    except Exception as helper_e:
                        avg_rating = None
                    current_album_for_artist['avg_rating'] = avg_rating if avg_rating is not None else 'Not rated'
                    if artist_name not in artists_dict:
                        artists_dict[artist_name] = {'name': artist_name, 'albums': []}
                    artists_dict[artist_name]['albums'].append(current_album_for_artist)
                results['artists'] = list(artists_dict.values())
            except KeyError as ke:
                messages.error(request, f"Error processing artist results due to missing data: {ke}")
            except Exception as e:
                messages.error(request, "Error processing artist results.")

        # --- Search Users (SUPABASE version) ---
        if search_type in ['all', 'users']:
            try:
                client = authenticate_with_jwt()
                if not client:
                    messages.error(request, "Could not connect to Supabase.")
                    results['users'] = []
                else:
                    # Query users from Supabase
                    user_response = client.table('soundscore_user') \
                        .select('id,username,profile_picture') \
                        .ilike('username', f'%{query}%') \
                        .limit(10) \
                        .execute()
                    user_data = user_response.data or []
                    user_list = []
                    for user in user_data:
                        supabase_user_id = user['id']
                        # Fetch reviews for this user from Supabase
                        review_response = client.table('soundscore_review') \
                            .select('rating') \
                            .eq('user_id', supabase_user_id) \
                            .execute()
                        review_data = review_response.data or []
                        review_count = len(review_data)
                        if review_count > 0:
                            avg_rating = round(
                                sum(r['rating'] for r in review_data if r.get('rating') is not None) / review_count, 1
                            )
                        else:
                            avg_rating = 'No ratings'
                        
                        # Ensure profile_picture is handled correctly
                        # Supabase storage URLs might need specific handling if not public
                        profile_picture_url = user.get('profile_picture') 
                        # If using Supabase storage and URLs aren't public, you might need 
                        # to generate signed URLs or ensure the bucket is public.
                        # For now, we assume the stored value is a direct URL or None.

                        user_list.append({
                            'username': user['username'],
                            'profile_picture_url': profile_picture_url, # Pass the URL/path to the template
                            'review_count': review_count,
                            'avg_rating': avg_rating
                        })
                    results['users'] = user_list
            except Exception as e:
                messages.error(request, f"Could not fetch user results from Supabase: {e}")


    context = {
        'query': query,
        'search_type': search_type,
        'results': results
    }
    return render(request, 'reviews/discover.html', context)

@login_required
def user_profile(request, username):
    client = authenticate_with_jwt()
    if not client:
        messages.error(request, "Could not connect to Supabase.")
        return redirect('home')

    # Get user from Supabase
    user_response = client.table('soundscore_user').select('id,username,profile_picture').eq('username', username).limit(1).execute()
    if not user_response.data:
        messages.error(request, f"User '{username}' not found in Supabase.")
        return redirect('home')
    profile_user = user_response.data[0]
    supabase_user_id = profile_user['id']

    # Get reviews by this user from Supabase, ordered by created_at desc
    reviews_response = client.table('soundscore_review') \
        .select('*, soundscore_album(title, artist, cover_image, spotify_id)') \
        .eq('user_id', supabase_user_id) \
        .order('created_at', desc=True) \
        .execute()
    user_reviews = reviews_response.data or []

    # Calculate review statistics
    review_count = len(user_reviews)
    if review_count > 0:
        avg_rating = round(
            sum(r['rating'] for r in user_reviews if r.get('rating') is not None) / review_count, 1
        )
    else:
        avg_rating = None

    context = {
        'profile_user': profile_user,
        'user_reviews': user_reviews,
        'review_count': review_count,
        'avg_rating': avg_rating,
        'is_own_profile': request.user.username == username
    }
    return render(request, 'reviews/user_profile.html', context)

# Helper

def get_album_avg_rating(spotify_id):
    try:
        db_album = Album.objects.filter(spotify_id=spotify_id).first()
        if db_album:
            avg_rating = Review.objects.filter(album=db_album).aggregate(Avg('rating'))['rating__avg']
            return round(avg_rating, 1) if avg_rating is not None else None
    except Album.DoesNotExist:
        pass
    return None

@cache_page(60)
@login_required
def feed(request):
    # Initialize reviews
    reviews = []
    
    client = authenticate_with_jwt()
    if not client:
        return render(request, 'reviews/feed.html', {'error': "Could not connect to Supabase."})
        
    try:
        # Fetch reviews - same as before
        reviews_response = client.table('soundscore_review')\
            .select('*, soundscore_album(*), soundscore_user(*)')\
            .order('created_at', desc=True)\
            .limit(10)  # REDUCED from 20 to 10
            
        # Execute the query
        reviews_response = reviews_response.execute()
        reviews = reviews_response.data or []
        
        # Get all review IDs at once
        review_ids = [review["id"] for review in reviews]
        
        # OPTIMIZATION 1: Batch fetch all comments at once
        if review_ids:
            all_comments = {}
            comments_response = client.table('soundscore_comment')\
                .select('*, soundscore_user(id, username, profile_picture)')\
                .in_('review_id', review_ids)\
                .order('created_at', desc=False)\
                .execute()
                
            # Group comments by review_id
            for comment in comments_response.data or []:
                review_id = comment['review_id']
                if review_id not in all_comments:
                    all_comments[review_id] = []
                all_comments[review_id].append(comment)
        
        # OPTIMIZATION 2: Batch count all likes at once
        all_likes = {}
        if review_ids:
            try:
                likes_count_response = client.table("soundscore_review_like")\
                    .select("review_id", count="exact")\
                    .in_("review_id", review_ids)\
                    .group_by('review_id')\
                    .execute()
                
                if likes_count_response.data:
                    for item in likes_count_response.data:
                        all_likes[item['review_id']] = item['count']
            except:
                # Fallback if group by fails
                for review_id in review_ids:
                    count_query = client.table("soundscore_review_like")\
                        .select("*", count="exact")\
                        .eq("review_id", review_id)\
                        .execute()
                    all_likes[review_id] = count_query.count if hasattr(count_query, 'count') else 0
                
        # OPTIMIZATION 3: If logged in, batch fetch user likes in one query
        user_liked_reviews = set()
        if request.user.is_authenticated and review_ids:
            user_resp = client.table("soundscore_user").select("id").eq("username", request.user.username).limit(1).execute()
            if user_resp.data:
                user_id = user_resp.data[0]["id"]
                user_likes = client.table("soundscore_review_like")\
                    .select("review_id")\
                    .eq("user_id", user_id)\
                    .in_("review_id", review_ids)\
                    .execute()
                
                user_liked_reviews = {like["review_id"] for like in user_likes.data or []}

        # Now assign all the data to each review
        for review in reviews:
            review_id = review["id"]
            # Assign comments (limited to 3 most recent)
            review["comments"] = all_comments.get(review_id, [])[:3] 
            review["comment_count"] = len(all_comments.get(review_id, []))
            
            # Assign like count
            review["like_count"] = all_likes.get(review_id, 0)
            
            # Assign liked status
            review["is_liked"] = review_id in user_liked_reviews
            
        # Render with optimized data
        return render(request, 'reviews/feed.html', {'reviews': reviews})
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return render(request, 'reviews/feed.html', {'error': f"Error fetching reviews: {str(e)}"})


