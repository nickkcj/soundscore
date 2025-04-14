from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('account/<str:username>/', views.account, name='account'),
    path('logout/', views.logout_view, name='logout'),
    path('reviews/<str:username>/', views.reviews, name='reviews'),
    path('reviews/<str:username>/create_review/', views.create_review, name='create_review'),
    path('api/search-albums/', views.search_albums_api_view, name='search_albums'),
    path('api/create-review/', views.create_review_api, name='create_review_api'),
    path('discover/', views.discover, name='discover'),
    path('profile/<str:username>/', views.user_profile, name='profile'),     
]

