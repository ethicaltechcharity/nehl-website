import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

from fixtures.forms import FixtureCancellationForm, MatchCardImageForm
from fixtures.models import Fixture, FixtureCancellation, MatchCardImage

from nehlwebsite.utils.auth_utils import can_manage_club


def index(request):
    return HttpResponse('')


def cancel(request, fixture_id):
    fixture = get_object_or_404(Fixture, pk=fixture_id)
    can_manage_fixture = False
    user = request.user

    if user.is_authenticated:
        if can_manage_club(user.id, fixture.team_a.club_id):
            can_manage_fixture = True
        if can_manage_club(user.id, fixture.team_b.club_id):
            can_manage_fixture = True

    if not can_manage_fixture:
        return HttpResponseForbidden()

    if request.method == 'POST':

        form = FixtureCancellationForm(request.POST)

        if form.is_valid():
            from fixtures.utils.cancellations import send_cancellation_notifications

            if form.cleaned_data['who_cancelled'] == "Home Team":
                team_cancellation = fixture.team_a
            else:
                team_cancellation = fixture.team_b

            now = datetime.datetime.now()
            cancellation = FixtureCancellation(
                cancellation_reporter=user.member,
                fixture=fixture,
                datetime_cancelled=now,
                cancellation_reason=form.cleaned_data['cancellation_reason'],
                more_info=form.cleaned_data['more_cancellation_info'],
                cancelled_by_team=team_cancellation
            )
            cancellation.save()

            send_cancellation_notifications(fixture, cancellation)

            return render(request, 'fixtures/cancellation_sent.html', {'fixture': fixture})

    elif request.method == 'GET':

        form = FixtureCancellationForm()

    else:
        return HttpResponseBadRequest()

    context = {
        'fixture': fixture,
        'form': form,
    }

    return render(request, 'fixtures/cancel.html', context)


def card_original(request):

    if request.method == 'POST':
        form = MatchCardImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'fixtures/match_card_upload_success.html', {})
    else:
        form = MatchCardImageForm()

    return render(request, 'fixtures/match_card_upload.html', {
        'form': form
    })


def match_card_originals(request):
    match_cards = MatchCardImage.objects.all()

    return render(request, 'fixtures/match_card_originals.html', {
        'match_cards': match_cards
    })


def detail(request, fixture_id):
    fixture = get_object_or_404(Fixture, pk=fixture_id)
    can_manage_fixture = False
    user = request.user

    if user.is_authenticated:
        if can_manage_club(user.id, fixture.team_a.club_id):
            can_manage_fixture = True
        if can_manage_club(user.id, fixture.team_b.club_id):
            can_manage_fixture = True

    return render(request, 'fixtures/detail.html', {'fixture': fixture, 'can_manage': can_manage_fixture})
