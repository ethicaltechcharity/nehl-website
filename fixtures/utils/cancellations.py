from fixtures.models import Fixture, FixtureCancellation, Competition
from fixtures.utils.general import get_most_senior_parent_competition

from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_cancellation_notifications(fixture: Fixture, cancellation: FixtureCancellation):
    def notify_officials(_competition: Competition):
        msg_html = render_to_string('email/fixture_cancellation_admin.html',
                                    {'fixture': fixture,
                                     'cancellation': cancellation})
        msg_plain = render_to_string('email/fixture_cancellation_admin.txt',
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
        msg_html = render_to_string('email/fixture_cancellation_club.html',
                                    {'fixture': fixture,
                                     'cancellation': cancellation})
        msg_plain = render_to_string('email/fixture_cancellation_club.txt',
                                     {'fixture': fixture,
                                      'cancellation': cancellation})
        team_a_officials = _fixture.team_a.club.clubmanagementposition_set.all()
        team_b_officials = _fixture.team_b.club.clubmanagementposition_set.all()

        for official in team_a_officials:
            send_mail(
                'Fixture Cancellation',
                msg_plain,
                'some@sender.com',
                [official.holder.user.email],
                html_message=msg_html,
            )
        for official in team_b_officials:
            send_mail(
                'Fixture Cancellation',
                msg_plain,
                'notifications@northeasthockeyleague.org',
                [official.holder.user.email],
                html_message=msg_html,
            )

    competition = fixture.competition
    ultimate_parent_competition = get_most_senior_parent_competition(competition)

    notify_officials(ultimate_parent_competition)
    notify_clubs(fixture)



