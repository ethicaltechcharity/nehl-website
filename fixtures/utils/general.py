import uuid
import os

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404


def get_most_senior_parent_competition(competition):
    direct_parent = competition.parent_competition

    if direct_parent is None:
        return competition

    return get_most_senior_parent_competition(direct_parent)


def has_config_item(competition, key):

    if len(competition.config.filter(key=key)) == 0:
        return False

    return competition.config.get(key=key).value


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('match_cards', filename)


def email_competition_admins(competition, subject: str, msg_plain: str, msg_html: str):
    for official in competition.officials.all():
        send_mail(
            subject,
            msg_plain,
            'notifications@northeasthockeyleague.org',
            [official.user.email],
            html_message=msg_html,
        )


def update_standings(fixture, result):
    from fixtures.models import LeagueStanding

    competition = fixture.competition
    season = fixture.season
    team_a_standing = LeagueStanding.objects.filter(
        league=competition, season=season, team=fixture.team_a
    )
    team_b_standing = LeagueStanding.objects.filter(
        league=competition, season=season, team=fixture.team_b
    )

    if team_a_standing.count() == 0:
        team_a_standing = LeagueStanding(
            league=competition, season=season, team=fixture.team_a
        )
    else:
        team_a_standing = team_a_standing[0]
    if team_b_standing.count() == 0:
        team_b_standing = LeagueStanding(
            league=competition, season=season, team=fixture.team_b
        )
    else:
        team_b_standing = team_b_standing[0]

    team_a_standing.total_points += result.team_a_points
    team_b_standing.total_points += result.team_b_points
    team_a_standing.goal_difference += result.team_a_score
    team_a_standing.goal_difference -= result.team_b_score
    team_b_standing.goal_difference += result.team_b_score
    team_b_standing.goal_difference -= result.team_a_score
    if result.winner is fixture.team_a:
        team_a_standing.num_won += 1
        team_b_standing.num_lost += 1
    elif result.draw:
        team_a_standing.num_drawn += 1
        team_b_standing.num_drawn += 1
    team_a_standing.num_played += 1
    team_b_standing.num_played += 1

    team_a_standing.save()
    team_b_standing.save()


def fill_fixture_result(result):
    if result.team_a_score > result.team_b_score:
        result.winner = result.fixture.team_a
        result.loser = result.fixture.team_b
        result.team_a_points = 3
        result.team_b_points = 0
        result.draw = False
    elif result.team_b_score > result.team_a_score:
        result.winner = result.fixture.team_b
        result.loser = result.fixture.team_a
        result.team_a_points = 0
        result.team_b_points = 3
        result.draw = False
    else:
        result.team_a_points = 1
        result.team_b_points = 1
        result.draw = True
    return result


def finalise_fixture(fixture):
    pass


def get_club_id(team_id: int) -> int:
    from teams.models import Team
    team = get_object_or_404(Team, pk=team_id)
    return team.club.id


def get_api_url(team_id: int):
    club_id = get_club_id(team_id)
    api_url = str.format('/clubs/api/{}/members/', club_id)
    return api_url


def can_submit_match_card(user, fixture):
    can_manage_team_a = False
    can_administrate = False

    from nehlwebsite.utils.auth_utils import can_manage_club, can_administrate_competition

    if user.is_authenticated:
        if can_manage_club(user.id, fixture.team_a.club.id):
            can_manage_team_a = True
        if can_administrate_competition(user.id, fixture.competition.id):
            can_administrate = True

    if not (can_administrate or can_manage_team_a):
        return False

    else:
        return True
