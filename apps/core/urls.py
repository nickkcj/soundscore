from django.urls import path
from .views import home
from .views import about

urlpatterns = [

    # Home URLS
    path('', home.home, name='home'),
    path('home/', home.home, name='home'),

    # About URLS
    path('about/', about.about, name='about'),
]