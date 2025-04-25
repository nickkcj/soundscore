from django.urls import path
from ..views import home

urlpatterns = [
    path('', home.home, name='home'),
    path('home/', home.home, name='home'),
    path('about/', home.about, name='about'),
    path('debug/', home.debug, name='debug'),
]