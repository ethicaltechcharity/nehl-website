from django.shortcuts import get_object_or_404, render
from teams.models import Team
from fixtures.models import Fixture
from django.db.models import Q


def detail(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    fixtures = Fixture.objects.filter(Q(team_a_id=team_id) | Q(team_b_id=team_id))
    return render(request, 'teams/detail.html', {'team': team, 'fixtures': fixtures})
