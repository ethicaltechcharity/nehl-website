from django.core.mail import send_mail


def email_notifications(recipients, subject, msg_plain, msg_html):
    send_mail(
        subject,
        msg_plain,
        'notifications@northeasthockeyleague.org',
        recipients,
        html_message=msg_html,
    )
