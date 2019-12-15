import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.core.paginator import Paginator

from fixtures.forms import FixtureCancellationForm, MatchCardImageForm
from fixtures.models import Fixture, FixtureCancellation, MatchCardImage
from fixtures.utils.general import has_config_item

from nehlwebsite.utils.auth_utils import can_manage_club, can_administrate_competition


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
    match_card_list = MatchCardImage.objects.order_by('-uploaded_at').all()

    paginator = Paginator(match_card_list, 25)

    page = request.GET.get('page')
    match_cards = paginator.get_page(page)

    return render(request, 'fixtures/match_card_originals.html', {
        'match_cards': match_cards
    })


def detail(request, fixture_id):
    fixture = get_object_or_404(Fixture, pk=fixture_id)
    can_manage_fixture = False
    can_administrate = False
    rearrangements_allowed = has_config_item(fixture.competition, 'rearrangements_allowed')
    user = request.user

    if user.is_authenticated:
        if can_manage_club(user.id, fixture.team_a.club.id):
            can_manage_fixture = True
        if can_manage_club(user.id, fixture.team_b.club.id):
            can_manage_fixture = True
        if can_administrate_competition(user.id, fixture.competition.id):
            can_administrate = True

    is_cancelled = fixture.fixturecancellation_set.count() > 0

    context = {
        'fixture': fixture,
        'can_manage': can_manage_fixture,
        'can_administrate': can_administrate,
        'rearrangements_allowed': rearrangements_allowed,
        'is_cancelled': is_cancelled
    }

    return render(request, 'fixtures/detail.html', context)
