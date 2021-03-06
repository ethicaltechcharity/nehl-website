from fixtures.models import Fixture, FixtureCancellation, Competition
from fixtures.utils.general import get_most_senior_parent_competition

from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_cancellation_notifications(fixture: Fixture, cancellation: FixtureCancellation):
    def notify_officials(_competition: Competition):
        msg_html = render_to_string('email/admin/fixture_cancellation.html',
                                    {'fixture': fixture,
                                     'cancellation': cancellation})
        msg_plain = render_to_string('email/admin/fixture_cancellation.txt',
                                     {'fixture': fixture,
                                      'cancellation': cancellation})

        for official in _competition.officials.all():
            send_mail(
                'Fixture Cancellation',
                msg_plain,
                'notifications@northeasthockeyleague.org',
                [official.user.email],
                html_message=msg_html,
            )

    def notify_clubs(_fixture: Fixture):
        msg_html = render_to_string('email/club/fixture_cancellation.html',
                                    {'fixture': fixture,
                                     'cancellation': cancellation})
        msg_plain = render_to_string('email/club/fixture_cancellation.txt',
                                     {'fixture': fixture,
                                      'cancellation': cancellation})
        team_a_officials = {_fixture.team_a.club.main_contact, _fixture.team_a.club.fixture_coordinator}
        team_b_officials = {_fixture.team_b.club.main_contact, _fixture.team_b.club.fixture_coordinator}

        for official in team_a_officials:
            if official is not None:
                send_mail(
                    'Fixture Cancellation',
                    msg_plain,
                    'notifications@northeasthockeyleague.org',
                    [official.user.email],
                    html_message=msg_html,
                )
        for official in team_b_officials:
            if official is not None:
                send_mail(
                    'Fixture Cancellation',
                    msg_plain,
                    'notifications@northeasthockeyleague.org',
                    [official.user.email],
                    html_message=msg_html,
                )

    competition = fixture.competition
    ultimate_parent_competition = get_most_senior_parent_competition(competition)

    notify_officials(ultimate_parent_competition)
    notify_clubs(fixture)


def can_manage_cancellation(cancellation: FixtureCancellation, user_id):

    a_fixture = cancellation.fixture
    for official in a_fixture.competition.officials.all():
        if official.user.id == user_id:
            return True
    parent_competition = get_most_senior_parent_competition(a_fixture.competition)
    for official in parent_competition.officials.all():
        if official.user.id == user_id:
            return True
