from django.urls import path
from ..views import users, reviews


urlpatterns = [
    path('register/', users.register, name='register'),
    path('login/', users.login, name='login'),
    path('logout/', users.logout_view, name='logout'),
    path('account/<str:username>/', users.account, name='account'),
    path('account/<str:username>/delete/', users.delete_account, name='delete_account'),
    path('account/<str:username>/delete/confirm/', users.delete_account_confirm, name='delete_account_confirm'),
    path('profile/<str:username>/', reviews.user_profile, name='profile'),
    
]
