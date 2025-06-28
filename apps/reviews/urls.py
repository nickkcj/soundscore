from django.urls import path
from .views import reviews, profile_views, spotify_views

urlpatterns = [
    path('', reviews.create_review_view, name='create_review'),
    path('api/create/', reviews.create_review_api_view, name='create_review_api'),
    path('api/search-albums/', spotify_views.search_albums_api_view, name='search_albums_api_alias'),
    path('edit/<str:review_id>/', reviews.edit_review_view, name='edit_review'),
    path('delete/<str:review_id>/', reviews.delete_review_view, name='delete_review'),
    path('<str:username>/', reviews.user_profile_view, name='reviews'),
    path('album/<str:spotify_id>/', reviews.album_detail_view, name='album_detail'),
]
