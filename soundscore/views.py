from django.shortcuts import render, HttpResponse
from .models import ToDo

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

#Whenever using a variable use double curly braces

def register(request):
    return render(request, 'register.html')


def login(request):
    return render(request, 'login.html')