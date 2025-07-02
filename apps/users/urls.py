from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('account/<str:username>/', views.account_view, name='account'),
    path('account/<str:username>/delete/', views.delete_account_view, name='delete_account'),
    path('account/<str:username>/delete/confirm/', views.delete_account_confirm_view, name='delete_account_confirm'),
    path('discover/', views.discover_view, name='discover'),
    path('profile/<str:username>/', views.user_profile, name='profile'),
    
    # Modal AJAX endpoints
    path('profile/<str:username>/followers-modal/', views.followers_modal, name='followers_list'),
    path('profile/<str:username>/following-modal/', views.following_modal, name='following_list'),
    
    # Follow/Unfollow AJAX endpoints
    path('profile/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('profile/<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
]