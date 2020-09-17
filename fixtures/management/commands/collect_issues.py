from datetime import datetime
from datetime import timedelta

from django.core.management import BaseCommand

from fixtures.models import Competition, Fixture, FixtureMetadata


def has_issue(fixture: Fixture):
    now = datetime.now()
    fixture_date = fixture.date
    when_submitted = fixture.metadata.time_match_card_complete
    match_card_leeway = timedelta(days=2)
    has_occurred = fixture_date < now.date()
    match_card_leeway_expired = False
    rearranged = fixture.rearrangement_to.count() > 0

    if has_occurred and not rearranged:
        if when_submitted is None:
            match_card_leeway_expired = (now.date() - fixture_date) > match_card_leeway
        else:
            match_card_leeway_expired = (when_submitted.date() - fixture_date) > match_card_leeway

    if match_card_leeway_expired:
        return True
    else:
        return False


class Command(BaseCommand):

    def handle(self, *args, **options):
        for competition in Competition.objects.all():
            if competition.current_season is None:
                continue

            fixtures = competition.current_season.fixture_set.all()

            print(competition)

            for fixture in fixtures:
                if fixture.metadata is None:
                    fixture.metadata = FixtureMetadata()
                    fixture.metadata.save()
                    fixture.save()
                if not fixture.metadata.issue_detected:
                    print(fixture)
                    if has_issue(fixture):
                        fixture.metadata.issue_detected = True
                        fixture.metadata.save()
