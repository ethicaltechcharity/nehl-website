from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.core.mail import send_mail
from django.template.loader import render_to_string

from clubs.models import Club, TransferRequest
from clubs.forms import TransferRequestForm

from nehlwebsite.utils.auth_utils import can_manage_club

import datetime


def index(request):
    clubs = Club.objects.order_by("name").all()
    return render(request, 'clubs/index.html', {'clubs': clubs})


def detail(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    can_manage = False
    user = request.user

    if user.is_authenticated:
        if can_manage_club(user.id, club_id):
            can_manage = True

    if club.secondary_colour == '#000000':
        light_or_dark = 'dark'
    else:
        light_or_dark = 'light'

    return render(request, 'clubs/detail.html',
                  {'club': club,
                   'can_manage': can_manage,
                   'light_or_dark': light_or_dark})


def manage(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    can_manage = False
    user = request.user

    if user.is_authenticated:
        if can_manage_club(user.id, club_id):
            can_manage = True

    if not can_manage:
        return HttpResponseForbidden()

    return render(request, 'clubs/manage.html', {'club': club})


def request_transfer(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    can_manage = False
    user = request.user

    if user.is_authenticated:
        if can_manage_club(user.id, club_id):
            can_manage = True

    if not can_manage:
        return HttpResponseForbidden()

    if request.method == 'POST':

        form = TransferRequestForm(request.POST, request.FILES)

        if form.is_valid():

            if 'evidence' in form.files:
                evidence = form.files['evidence']
            else:
                evidence = None

            now = datetime.datetime.now()
            transfer_request = TransferRequest(
                datetime_submitted=now,
                submitter=user.member,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                transfer_from=form.cleaned_data['transfer_from'],
                transfer_to=club,
                evidence=evidence
            )
            transfer_request.save()

            msg_html = render_to_string('email/transfer-request-email.html',
                                        {'request': transfer_request})
            msg_plain = render_to_string('email/transfer-request-email.txt',
                                         {'request': transfer_request})

            send_mail(
                'Transfer Request',
                msg_plain,
                'notifications@northeasthockeyleague.org',
                ['danbaxter@live.co.uk', 'leighbrown@hotmail.co.uk'],
                html_message=msg_html,
            )

            return render(request, 'clubs/members/transfer-request-sent.html')

    elif request.method == 'GET':

        form = TransferRequestForm()

    else:
        return HttpResponseBadRequest()

    return render(request, 'clubs/members/transfer-request.html', {'form': form})
