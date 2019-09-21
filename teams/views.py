from django.shortcuts import get_object_or_404, render
from teams.models import Team
from fixtures.models import Fixture
from django.db.models import Q
import datetime


def detail(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    fixtures = Fixture.objects.filter(Q(team_a_id=team_id) | Q(team_b_id=team_id)).order_by('date')
    can_manage_team = False
    user = request.user

    if user.is_authenticated:
        try:
            if user.member is not None:
                for position in user.member.management_position.all():
                    if user.member.club_id == team.club.id:
                        can_manage_team = True
        except:
            pass

    now = datetime.datetime.now()

    upcoming_fixtures = fixtures.filter(Q(date__gte=now))
    past_fixtures = fixtures.filter(Q(date__lt=now))

    if team.club.secondary_colour == '#000000':
        light_or_dark = 'dark'
    else:
        light_or_dark = 'light'

    return render(request, 'teams/detail.html',
                  {
                      'team': team,
                      'upcoming_fixtures': upcoming_fixtures,
                      'past_fixtures': past_fixtures,
                      'can_manage': can_manage_team,
                      'light_or_dark': light_or_dark
                  })
