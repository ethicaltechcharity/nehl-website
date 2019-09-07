from django.shortcuts import get_object_or_404, render
from clubs.models import Club


def index(request):
    clubs = Club.objects.order_by("name").all()
    return render(request, 'clubs/index.html', {'clubs': clubs})


def view(request):
    return render(request, 'clubs/view.html')


def detail(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    return render(request, 'clubs/detail.html', {'club': club})
