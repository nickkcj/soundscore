from django.shortcuts import render, HttpResponse, redirect
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

#Whenever using a variable use double curly braces

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        print(username, email, password, confirm_password)

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'register.html')
        
        try:
            password = make_password(password) 
            user = User.objects.create(username=username, email=email, password=password)
            user.save()
            messages.success(request, "User registered successfully!")
            return redirect('login')  
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('register')
        
    return render(request, 'register.html')


def login(request):
    return render(request, 'login.html')