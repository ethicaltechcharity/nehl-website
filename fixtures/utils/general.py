import uuid
import os

from django.core.mail import send_mail


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
