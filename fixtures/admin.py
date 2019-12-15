from django.contrib import admin
from fixtures.models import *

# Register your models here.

admin.site.register([Season, Competition, Fixture, Venue, Umpire,
                     CompetitionOfficial, CompetitionConfigItem, Rule, RuleSet, RuleParagraph, Penalty,
                     FixtureCancellation, FixtureRearrangement])
