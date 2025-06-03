from django.urls import path, include
from . import views
from .swagger import urlpatterns as swagger_urls

urlpatterns = [
    # Autenticação
    path('register/', views.RegisterView.as_view(), name='api_register'),
    path('login/', views.LoginView.as_view(), name='api_login'),
    
    # Perfil de usuário
    path('users/<str:username>/', views.UserProfileView.as_view(), name='api_user_profile'),
    path('users/<str:username>/delete/', views.DeleteUserView.as_view(), name='api_delete_user'),

    # Documentação Swagger
    path('docs/', include(swagger_urls)),

]