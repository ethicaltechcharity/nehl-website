from django.shortcuts import render


def index(request):
    return render(request, 'home/index.html', {})


def profile(request):
    return render(request, 'registration/profile.html', {})


def rules(request):
    return render(request, 'home/rules.html', {})
