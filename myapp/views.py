from django.shortcuts import render, HttpResponse
from .models import ToDo

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return HttpResponse("This is the about page.")

#Whenever using a variable use double curly braces

def todos(request):
    items = ToDo.objects.all()
    return render(request, 'todos.html', {
        'todos': items
    })