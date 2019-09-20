import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

from fixtures.forms import FixtureCancellationForm, MatchCardImageForm
from fixtures.models import Fixture, FixtureCancellation


def index(request):
    return HttpResponse('')


def cancel(request, fixture_id):
    fixture = get_object_or_404(Fixture, pk=fixture_id)
    can_manage_fixture = False
    user = request.user

    if user.is_authenticated:
        try:
            if user.member is not None:
                for position in user.member.management_position.all():
                    if user.member.club_id == fixture.team_a.club_id or user.member.club_id == fixture.team_b.club_id:
                        can_manage_fixture = True
        except:
            pass

    if not can_manage_fixture:
        return HttpResponseForbidden()

    if request.method == 'POST':

        form = FixtureCancellationForm(request.POST)

        if form.is_valid():
            from fixtures.utils.cancellations import send_cancellation_notifications

            now = datetime.datetime.now()
            cancellation = FixtureCancellation(
                cancellation_reporter=user.member,
                fixture=fixture,
                datetime_cancelled=now,
                cancellation_reason=form.cleaned_data['cancellation_reason'],
                more_info=form.cleaned_data['more_cancellation_info']
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


def detail(request, fixture_id):
    fixture = get_object_or_404(Fixture, pk=fixture_id)
    can_manage_fixture = False
    user = request.user

    if user.is_authenticated:
        try:
            if user.member is not None:
                for position in user.member.management_position.all():
                    if user.member.club_id == fixture.team_a.club_id or user.member.club_id == fixture.team_b.club_id:
                        can_manage_fixture = True
        except:
            pass

    return render(request, 'fixtures/detail.html', {'fixture': fixture, 'can_manage': can_manage_fixture})
