from django.contrib import admin
from fixtures.models import *

# Register your models here.

admin.site.register([Season, Competition, Fixture, Venue, Umpire,
                     CompetitionOfficial, Rule, RuleSet, RuleParagraph, Penalty, FixtureCancellation])
