from django.shortcuts import render

def about(request):
    """Render the About page."""
    return render(request, 'core/about.html')