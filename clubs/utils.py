from django.contrib.auth.models import User

from clubs.models import Club

from nehlwebsite.utils.general import email_notifications


def email_main_club_contacts(club: Club, subject: str, msg_plain: str, msg_html: str):
    officials = []

    if club.main_contact is not None:
        officials.append(club.main_contact.user.email)
    if club.fixture_coordinator is not None:
        officials.append(club.fixture_coordinator.user.email)

    if len(officials) > 0:
        email_notifications(
            officials,
            subject,
            msg_plain,
            msg_html
        )


def can_administrate_club(user: User, club: Club) -> bool:
    for team in club.team_set.all():
        for competition in team.involved_in.all():
            for official in competition.officials.all():
                if official.user == user:
                    return True
    return False
