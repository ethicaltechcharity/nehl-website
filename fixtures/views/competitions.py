from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, FormView, TemplateView

from clubs.models import Club
from fixtures.forms import SeasonCreateForm
from fixtures.models import Competition, LeagueStanding, Season, Fixture
from nehlwebsite.utils.auth_utils import can_administrate_competition
from teams.models import Team

import pandas
from datetime import datetime


class CompetitionListView(ListView):
    model = Competition
    context_object_name = 'competitions'
    template_name = 'competitions/list.html'


class CompetitionDetailView(DetailView):
    model = Competition
    context_object_name = 'competition'
    template_name = 'competitions/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['standings'] = LeagueStanding.objects \
            .filter(league=context[self.context_object_name],
                    season=context[self.context_object_name].season_set.first()) \
            .order_by('-total_points')
        context['seasons'] = Season.objects\
            .filter(competition=context[self.context_object_name])
        return context


class CompetitionAdminView(LoginRequiredMixin, TemplateView):
    template_name = 'competitions/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['competition'] = Competition.objects.get(pk=kwargs['competition'])
        return context

    def get(self, request, *args, **kwargs):
        if not can_administrate_competition(request.user.id, kwargs['competition']):
            return HttpResponseForbidden()

        return super().get(request, *args, **kwargs)


class CompetitionStandingsView(ListView):
    model = LeagueStanding
    context_object_name = 'standings'
    template_name = 'competitions/standings.html'

    def get_queryset(self):
        return LeagueStanding.objects\
            .filter(league_id=self.kwargs['competition'],
                    season_id=self.kwargs['season']) \
            .order_by('-total_points')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['competition'] = get_object_or_404(Competition,
                                                   pk=self.kwargs['competition'])
        context['season'] = get_object_or_404(Season,
                                              pk=self.kwargs['season'])
        return context

    def get(self, request, *args, **kwargs):
        if not can_administrate_competition(request.user.id, kwargs['competition']):
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)


class SeasonCreateView(LoginRequiredMixin, FormView):
    form_class = SeasonCreateForm
    template_name = 'competitions/seasons/create.html'

    def post(self, request, *args, **kwargs):
        if not can_administrate_competition(request.user.id, kwargs['competition']):
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        display_name = form.cleaned_data['display_name']
        years = form.cleaned_data['years']
        competition = Competition.objects.get(pk=self.kwargs['competition'])
        season = Season(display_name=display_name,
                        years=years,
                        competition=competition)
        season.save()
        form.files['fixtures_file'].seek(0)
        data = pandas.read_csv(form.files['fixtures_file'])
        for n, row in data.iterrows():
            date_str = row['date']
            club_a_str = row['club_a']
            team_a_str = row['team_a']
            club_b_str = row['club_b']
            team_b_str = row['team_b']

            club_a = Club.objects.get(short_name__iexact=club_a_str)
            club_b = Club.objects.get(short_name__iexact=club_b_str)

            team_a = Team.objects.get(club=club_a, short_name__iexact=team_a_str)
            team_b = Team.objects.get(club=club_b, short_name__iexact=team_b_str)

            date = datetime.strptime(date_str, '%d/%m/%Y')

            fixture = Fixture(
                team_a=team_a,
                team_b=team_b,
                date=date,
                season=season,
                competition=competition
            )

            season.teams.add(team_a, team_b)

            fixture.save()

        season.save()

        for team in season.teams.all():
            standing = LeagueStanding(
                league=competition,
                team=team,
                season=season,
                num_played=0,
                num_won=0,
                num_lost=0,
                num_drawn=0,
                goal_difference=0,
                total_points=0
            )
            standing.save()

        return super().form_valid(form)


class SeasonAdminView(LoginRequiredMixin, TemplateView):
    template_name = 'competitions/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['competition'] = Competition.objects.get(pk=kwargs['competition'])
        return context

    def get(self, request, *args, **kwargs):
        if not can_administrate_competition(request.user.id, kwargs['competition']):
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)


class SeasonIssuesView(LoginRequiredMixin, ListView):
    template_name = 'competitions/seasons/issues.html'
    context_object_name = 'fixtures'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        competition = Competition.objects.get(pk=self.kwargs['competition'])
        season = Season.objects.get(pk=self.kwargs['season'])
        context['season'] = season
        context['competition'] = competition
        return context

    def get_queryset(self):
        season = Season.objects.get(pk=self.kwargs['season'])
        fixtures = season.fixture_set.filter(metadata__issue_detected=True)
        return fixtures


    def get(self, request, *args, **kwargs):
        if not can_administrate_competition(request.user.id, kwargs['competition']):
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)
