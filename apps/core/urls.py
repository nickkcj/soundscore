from django.urls import path
from .views import home
from .views import about

urlpatterns = [
    path('', home.home, name='home'),
    path('home/', home.home, name='home'),
    path('about/', about.about, name='about'),
]