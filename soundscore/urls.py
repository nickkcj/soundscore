from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    # path('home/', views.home, name='home'), # Remove duplicate
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('account/<str:username>/', views.account, name='account'),

    # Add the logout URL pattern
    path('logout/', views.logout_view, name='logout'),
    path('reviews/<str:username>/', views.reviews, name='reviews'),
    path('reviews/<str:username>/create_review/', views.create_review, name='create_review'),
]

