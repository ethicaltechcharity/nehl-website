from datetime import datetime
from datetime import timedelta

from django.core.management import BaseCommand

from fixtures.models import Competition, Fixture, FixtureMetadata
from teams.models import Team


class Command(BaseCommand):
    def handle(self, *args, **options):
        for fixture in Fixture.objects.all():
            if fixture.season.years == '202021' \
                    and ((fixture.team_a.id == 112 or fixture.team_b.id == 112)     # Medics 2s
                         or (fixture.team_a.id == 113 or fixture.team_b.id == 113)):    # Medics 3s
                medics_2s = Team.objects.get(pk=112)
                medics_3s = Team.objects.get(pk=113)
                if fixture.team_a.id == 112:
                    fixture.team_a = medics_3s
                elif fixture.team_a.id == 113:
                    fixture.team_a = medics_2s
                if fixture.team_b.id == 112:
                    fixture.team_b = medics_3s
                elif fixture.team_b.id == 113:
                    fixture.team_b = medics_2s

                fixture.save()
