from django.urls import path
from ..views import reviews

urlpatterns = [
    path('discover/', reviews.discover, name='discover'),
    path('create/<str:username>/', reviews.create_review, name='create_review'),
    path('edit/<str:review_id>/', reviews.edit_review, name='edit_review'),
    path('delete-review/<str:review_id>/', reviews.delete_review, name='delete_review'),
    path('search/albums/', reviews.search_albums_api_view, name='search_albums_api'),
    path('api/search-albums/', reviews.search_albums_api_view, name='search_albums_api_alias'),
    path('api/create-review/', reviews.create_review_api, name='create_review_api_alias'),  # Optional extra alias
    path('user/<str:username>/', reviews.user_profile, name='user_profile'),
    path('<str:username>/', reviews.reviews, name='reviews'),  # Always last
]


