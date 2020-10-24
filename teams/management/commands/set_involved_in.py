from django.core.management import BaseCommand

from teams.models import Team


class Command(BaseCommand):
    def handle(self, *args, **options):
        for team in Team.objects.all():
            for fixture in team.team_a_fixtures.all():
                if not team.involved_in.filter(pk=fixture.competition.id).exists():
                    team.involved_in.add(fixture.competition)
            for fixture in team.team_b_fixtures.all():
                if not team.involved_in.filter(pk=fixture.competition.id).exists():
                    team.involved_in.add(fixture.competition)
            team.save()
