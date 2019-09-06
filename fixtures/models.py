from django.db import models
from django.conf import settings


class Season(models.Model):
    years = models.CharField(max_length=6)
    display_name = models.CharField(max_length=7)

    def __str__(self):
        return self.display_name


class Competition(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=5)
    parent_competition = models.ForeignKey('Competition',
                                           on_delete=models.SET_NULL,
                                           null=True,
                                           related_name='child_competition',
                                           blank=True
                                           )
    officials = models.ManyToManyField('CompetitionOfficial')

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=50)
    street_name = models.CharField(max_length=50, default='')
    postcode = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class VenueUseType(models.Model):
    user = models.ForeignKey('clubs.Club', on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    use_type = models.CharField(max_length=30)


class Fixture(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    team_a = models.ForeignKey('teams.Team',
                               related_name='team_a_fixtures',
                               on_delete=models.CASCADE,
                               null=True
                               )
    team_b = models.ForeignKey('teams.Team',
                               related_name='team_b_fixtures',
                               on_delete=models.CASCADE,
                               null=True
                               )
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    umpire_a = models.ForeignKey('Umpire',
                                 related_name='fixtures_as_umpire_a',
                                 on_delete=models.SET_NULL,
                                 null=True)
    umpire_b = models.ForeignKey('Umpire',
                                 related_name='fixtures_as_umpire_b',
                                 on_delete=models.SET_NULL,
                                 null=True)

    def __str__(self):
        return self.date.__str__() + ' - ' + self.team_a.__str__() + " vs " + self.team_b.__str__()


class FixtureCancellation(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    datetime_cancelled = models.DateTimeField()
    cancellation_reason = models.CharField(max_length=30)


class Official(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.SET_NULL,
                                null=True)

    class Meta:
        abstract = True


class MatchOfficial(Official):
    pass


class Umpire(MatchOfficial):
    pass


class CompetitionOfficial(Official):
    pass
