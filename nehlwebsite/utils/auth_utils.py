from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from clubs.models import Club

from fixtures.models import Competition

from fixtures.utils.general import get_most_senior_parent_competition


def can_manage_club(user_id: int, club_id: int) -> bool:
    user = get_object_or_404(User, pk=user_id)
    club = get_object_or_404(Club, pk=club_id)

    try:
        if user.member is not None:
            for _ in user.member.management_position.all():
                if user.member.club_id == club_id or user.member.club_id == club_id:
                    return True
        for team in club.team_set.all():
            if team.team_a_fixtures.count() > 0:
                a_fixture = team.team_a_fixtures.first()
                for official in a_fixture.competition.officials.all():
                    if official.user.id == user_id:
                        return True
                parent_competition = get_most_senior_parent_competition(a_fixture.competition)
                for official in parent_competition.officials.all():
                    if official.user.id == user_id:
                        return True
    except:
        return False

    return False


def can_administrate_competition(user_id: int, competition_id: int) -> bool:
    competition = get_object_or_404(Competition, pk=competition_id)

    while True:
        for official in competition.officials.all():
            if official.user.id == user_id:
                return True
        if competition.parent_competition is None:
            break
        competition = competition.parent_competition

    return False
