from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseForbidden, HttpResponseBadRequest

from clubs.models import Club, TransferRequest
from clubs.forms import TransferRequestForm

import datetime


def index(request):
    clubs = Club.objects.order_by("name").all()
    return render(request, 'clubs/index.html', {'clubs': clubs})


def view(request):
    return render(request, 'clubs/view.html')


def detail(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    can_manage_club = False
    user = request.user

    if user.is_authenticated:
        try:
            if user.member is not None:
                for position in user.member.management_position.all():
                    if user.member.club_id == club.id:
                        can_manage_club = True
        except:
            pass

    return render(request, 'clubs/detail.html',
                  {'club': club, 'can_manage': can_manage_club})


def manage(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    can_manage_club = False
    user = request.user

    if user.is_authenticated:
        try:
            if user.member is not None:
                for position in user.member.management_position.all():
                    if user.member.club_id == club.id:
                        can_manage_club = True
        except:
            pass

    if not can_manage_club:
        return HttpResponseForbidden()

    return render(request, 'clubs/manage.html', {'club': club})


def request_transfer(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    can_manage_club = False
    user = request.user

    if user.is_authenticated:
        try:
            if user.member is not None:
                for position in user.member.management_position.all():
                    if user.member.club_id == club.id:
                        can_manage_club = True
        except:
            pass

    if not can_manage_club:
        return HttpResponseForbidden()

    if request.method == 'POST':

        form = TransferRequestForm(request.POST)

        if form.is_valid():

            now = datetime.datetime.now()
            request = TransferRequest(
                datetime_submitted=now,
                submitter=user.member,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                transfer_from=form.transfer_from,
                transfer_to=user.member.club,
                evidence=form.files['evidence']
            )
            request.save()

            return render(request, 'clubs/members/transfer-request-sent.html')

    elif request.method == 'GET':

        form = TransferRequestForm()

    else:
        return HttpResponseBadRequest()

    return render(request, 'clubs/members/transfer-request.html', {'form': form})
