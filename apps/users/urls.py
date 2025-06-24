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
] 