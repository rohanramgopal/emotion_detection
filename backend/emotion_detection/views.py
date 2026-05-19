from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def analysis(request):
    return render(request, 'analysis.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def login_view(request):
    return render(request, 'login.html')
def register(request):
    return render(request, 'register.html')