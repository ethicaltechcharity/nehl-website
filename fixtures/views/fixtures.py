import datetime
import itertools

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.views.generic import FormView

from fixtures.forms import *
from fixtures.models import Fixture, FixtureCancellation, MatchCardImage, Appearance, Player, Goal, PersonalPenalty, \
    FixtureMetadata
from fixtures.utils.general import has_config_item, fill_fixture_result, update_standings, can_submit_match_card

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
    can_manage_team_a = False
    can_manage_team_b = False
    can_administrate = False
    rearrangements_allowed = has_config_item(fixture.competition, 'rearrangements_allowed')
    user = request.user

    if fixture.metadata is None:
        fixture.metadata = FixtureMetadata()

    if user.is_authenticated:
        if can_manage_club(user.id, fixture.team_a.club.id):
            can_manage_fixture = True
            can_manage_team_a = True
        if can_manage_club(user.id, fixture.team_b.club.id):
            can_manage_fixture = True
            can_manage_team_b = True
        if can_administrate_competition(user.id, fixture.competition.id):
            can_administrate = True

    metadata = fixture.metadata

    has_occurred = fixture.date <= datetime.now().date()

    squad_a_selected = metadata.squad_a_selected
    squad_b_selected = metadata.squad_b_selected
    squads_selected = squad_a_selected and squad_b_selected

    can_select_squad_a = not squad_a_selected and (can_manage_team_a or can_administrate)
    can_select_squad_b = not squad_b_selected and ((can_manage_team_a and has_occurred)
                                                   or can_manage_team_b or can_administrate)

    match_card_completed = squads_selected and metadata.match_card_image is not None \
                           and metadata.personal_penalties_submitted and metadata.scorers_submitted

    can_complete_card = squads_selected and not match_card_completed and has_occurred \
                        and (can_manage_team_a or can_administrate)

    is_cancelled = fixture.fixturecancellation_set.count() > 0

    squad_a = Appearance.objects.filter(fixture=fixture, team=fixture.team_a)
    squad_b = Appearance.objects.filter(fixture=fixture, team=fixture.team_b)

    squads = itertools.zip_longest(squad_a, squad_b)

    context = {
        'fixture': fixture,
        'squads': squads,
        'can_manage': can_manage_fixture,
        'can_select_squad_a': can_select_squad_a,
        'can_select_squad_b': can_select_squad_b,
        'can_complete_card': can_complete_card,
        'squad_a_selected': squad_a_selected,
        'squad_b_selected': squad_b_selected,
        'squads_selected': squads_selected,
        'card_complete': match_card_completed,
        'can_administrate': can_administrate,
        'has_occurred': has_occurred,
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


class SelectSquadView(LoginRequiredMixin, FormView):
    template_name = 'fixtures/select_squad.html'
    form_class = AppearanceForm

    def get_success_url(self):
        return '/fixtures/' + str(self.kwargs['fixture_id'])

    def get_context_data(self, **kwargs):

        formset = kwargs.get('formset')
        if formset is None:
            formset = AppearancesFormset(form_kwargs=self.kwargs)

        fixture_id = self.kwargs['fixture_id']
        team_id = self.kwargs['team_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)
        team = get_object_or_404(Team, pk=team_id)

        context = {
            'formset': formset,
            'fixture': fixture,
            'team': team,
            'club_id': team.club.id,
            'helper': AppearanceFormHelper(),
            'formset_js_url': static('js/jquery.formset.js'),
            'page_js': static('fixtures/select_squad.js')
        }

        return context

    def post(self, request, *args, **kwargs):
        formset = AppearancesFormset(request.POST, form_kwargs=self.kwargs)
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        fixture_id = self.kwargs['fixture_id']
        team_id = self.kwargs['team_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)
        team = get_object_or_404(Team, pk=team_id)

        for form in formset:
            data = form.cleaned_data
            if 'is_registered' in data:
                if data['is_registered']:
                    member = data['member']
                    query_set = Player.objects.filter(member=member)
                    if query_set.count() > 0:
                        player = query_set[0]
                    else:
                        player = Player(member=member)
                        player.save()
                else:
                    first_name = data['first_name']
                    last_name = data['last_name']
                    query_set = Player.objects.filter(first_name=first_name, last_name=last_name)
                    if query_set.count() > 0:
                        player = query_set[0]
                    else:
                        player = Player(first_name=first_name, last_name=last_name)
                        player.save()

                appearance = Appearance(
                    player=player,
                    fixture=fixture,
                    team=team,
                )
                appearance.save()

        if team == fixture.team_a:
            if fixture.metadata is None:
                fixture.metadata = FixtureMetadata()
            fixture.metadata.squad_a_selected = True
            fixture.metadata.time_squad_a_selected = datetime.now()
            fixture.metadata.save()
        elif team == fixture.team_b:
            if fixture.metadata is None:
                fixture.metadata = FixtureMetadata()
            fixture.metadata.squad_b_selected = True
            fixture.metadata.time_squad_b_selected = datetime.now()
            fixture.metadata.save()
        else:
            raise AttributeError()
        fixture.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))


class SubmitScorersView(LoginRequiredMixin, FormView):
    form_class = ScorerForm
    template_name = 'fixtures/submit_scorers.html'

    def get_success_url(self):
        return '/fixtures/' + str(self.kwargs['fixture_id']) + '/submit-match-card'

    def get_context_data(self, **kwargs):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        formset = kwargs.get('formset')
        if formset is None:
            formset = ScorerFormset(form_kwargs={'fixture': fixture})

        context = {
            'formset': formset,
            'fixture': fixture,
            'helper': ScorerFormsetHelper(),
            'formset_js_url': static('js/jquery.formset.js'),
            # 'page_js': static('fixtures/select_squad.js')
        }

        return context

    def get_form_kwargs(self):
        return {
            'fixture': Fixture.objects.get(pk=self.kwargs['fixture_id'])
        }

    def get(self, request, *args, **kwargs):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if fixture.metadata.scorers_submitted:
            return HttpResponseRedirect(self.get_success_url())

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if not can_submit_match_card(request.user, fixture):
            return HttpResponseForbidden()

        formset = ScorerFormset(request.POST, form_kwargs={'fixture': fixture})
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if fixture.result is None:
            result = FixtureResult()
            result.save()
        else:
            result = fixture.result

        team_a_goals = 0
        team_b_goals = 0

        for form in formset:
            data = form.cleaned_data

            if 'scorer' in data and 'number' in data:
                scorer = data['scorer']
                goals = data['number']
                for n in range(0, goals):
                    goal = Goal(
                        appearance=scorer,
                        fixture=result
                    )
                    goal.save()

                if scorer.team == fixture.team_a:
                    team_a_goals += goals
                elif scorer.team == fixture.team_b:
                    team_b_goals += goals
                else:
                    raise Exception()

        if not result.complete:
            result.team_a_score = team_a_goals
            result.team_b_score = team_b_goals

            result = fill_fixture_result(result)
            result.save()
            fixture.result = result
            fixture.save()

            update_standings(fixture, result)

        fixture.metadata.scorers_submitted = True
        fixture.metadata.time_scorers_submitted = datetime.now()
        fixture.metadata.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))


class SubmitPenaltiesView(LoginRequiredMixin, FormView):
    form_class = PenaltyForm
    template_name = 'fixtures/submit_penalties.html'

    def get_success_url(self):
        return '/fixtures/' + str(self.kwargs['fixture_id']) + '/submit-scorers'

    def get_context_data(self, **kwargs):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        formset = kwargs.get('formset')
        if formset is None:
            formset = PenaltyFormset(form_kwargs={'fixture': fixture})

        context = {
            'formset': formset,
            'fixture': fixture,
            'helper': PenaltyFormsetHelper(),
            'formset_js_url': static('js/jquery.formset.js'),
            # 'page_js': static('fixtures/select_squad.js')
        }

        return context

    def get_form_kwargs(self):
        return {
            'fixture': Fixture.objects.get(pk=self.kwargs['fixture_id'])
        }

    def get(self, request, *args, **kwargs):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if fixture.metadata.personal_penalties_submitted:
            return HttpResponseRedirect(self.get_success_url())

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if not can_submit_match_card(request.user, fixture):
            return HttpResponseForbidden()

        formset = PenaltyFormset(request.POST, form_kwargs={'fixture': fixture})
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if fixture.result is None:
            result = FixtureResult()
            result.save()
            fixture.result = result
            fixture.save()
        else:
            result = fixture.result

        for form in formset:
            data = form.cleaned_data

            if 'recipient' in data and 'type' in data:
                recipient = data['recipient']
                penalty_type = data['type']

                penalty = PersonalPenalty(
                    appearance=recipient,
                    fixture=result,
                    penalty_type=penalty_type
                )
                penalty.save()

        fixture.metadata.personal_penalties_submitted = True
        fixture.metadata.time_penalties_submitted = datetime.now()
        fixture.metadata.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))


class SubmitMatchCardView(LoginRequiredMixin, FormView):
    form_class = MatchCardForm
    template_name = 'fixtures/submit_match_card.html'

    def get_success_url(self):
        return '/fixtures/' + str(self.kwargs['fixture_id'])

    def get_context_data(self, **kwargs):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        form = kwargs.get('form')
        if form is None:
            form = MatchCardForm(form)

        context = {
            'form': form,
            'fixture': fixture,
            'formset_js_url': static('js/jquery.formset.js'),
            # 'page_js': static('fixtures/select_squad.js')
        }

        return context

    def get(self, request, *args, **kwargs):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if fixture.metadata.match_card_image_submitted:
            return HttpResponseRedirect(self.get_success_url())

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if not can_submit_match_card(request.user, fixture):
            return HttpResponseForbidden()

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if fixture.metadata is None:
            metadata = FixtureMetadata()
            fixture.metadata = metadata
            fixture.save()
        else:
            metadata = fixture.metadata

        metadata.captain_a_signed = form.cleaned_data['captain_a_signed']
        metadata.captain_b_signed = form.cleaned_data['captain_b_signed']
        metadata.umpire_a_signed = form.cleaned_data['umpire_a_signed']
        metadata.umpire_b_signed = form.cleaned_data['umpire_b_signed']
        metadata.match_card_image = form.cleaned_data['image']
        metadata.match_card_image_submitted = True
        metadata.time_match_card_image_submitted = datetime.now()
        metadata.time_match_card_complete = datetime.now()
        metadata.save()

        return HttpResponseRedirect(self.get_success_url())


