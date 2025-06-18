from django.urls import path
from .views import reviews, profile_views, spotify_views

urlpatterns = [
    path('', reviews.create_review_view, name='create_review'),
    path('api/create/', reviews.create_review_api_view, name='create_review_api'),
    path('edit/<int:review_id>/', reviews.edit_review_view, name='edit_review'),
    path('delete/<int:review_id>/', reviews.delete_review_view, name='delete_review'),
    path('<str:username>/', profile_views.user_profile_view, name='reviews'),
]
