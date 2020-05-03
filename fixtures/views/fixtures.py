import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView

from fixtures.forms import *
from fixtures.models import Fixture, FixtureCancellation, MatchCardImage
from fixtures.utils.general import has_config_item, get_club_id

from nehlwebsite.utils.auth_utils import can_manage_club, can_administrate_competition


@login_required
def index(request):
    return HttpResponse('')


@login_required
def cancel(request, fixture_id):
    fixture = get_object_or_404(Fixture, pk=fixture_id)
    can_manage_fixture = False
    user = request.user

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


@login_required
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


@login_required
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


@login_required
def submit_result(request, fixture_id):
    fixture = get_object_or_404(Fixture, pk=fixture_id)
    can_manage_fixture = False
    can_administrate = False
    user = request.user

    if can_manage_club(user.id, fixture.team_a.club.id):
        can_manage_fixture = True
    if can_manage_club(user.id, fixture.team_b.club.id):
        can_manage_fixture = True
    if can_administrate_competition(user.id, fixture.competition.id):
        can_administrate = True

    if not can_manage_fixture and not can_administrate:
        return HttpResponseForbidden()

    if request.method == "POST":

        form = SubmitResultForm(data=request.POST, fixture=fixture)

        if form.is_valid():

            from fixtures.utils.general import fill_fixture_result

            form.instance.fixture = fixture
            form.instance = fill_fixture_result(form.instance)
            saved = form.save()

            fixture.result = saved
            fixture.save()

            return redirect('fixtures:detail', fixture_id=fixture.id)

    elif request.method == "GET":
        form = SubmitResultForm(fixture)

    else:
        return HttpResponseBadRequest()

    context = {
        'form': form,
        'fixture': fixture
    }

    return render(request, 'fixtures/submit_result.html', context)


class SelectSquadView(FormView):
    template_name = 'fixtures/select_squad.html'
    form_class = AppearanceForm

    def get_context_data(self, **kwargs):
        context = {
            'formset': AppearancesFormset(form_kwargs=self.kwargs),
            'club_id': get_club_id(self.kwargs['team_id']),
            'helper': AppearanceFormHelper()
        }
        return context

    def post(self, request, *args, **kwargs):
        formset = AppearancesFormset(**self.get_form_kwargs())
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))
