from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import DetailView

from fixtures.models import Competition, LeagueStanding


@login_required
def index(request):
    return HttpResponse('')


class CompetitionDetailView(DetailView):
    model = Competition
    context_object_name = 'competition'
    template_name = 'competitions/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['standings'] = LeagueStanding.objects\
            .filter(league=context[self.context_object_name])\
            .order_by('total_points')
        return context
