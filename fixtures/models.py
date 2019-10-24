from django.db import models
from django.conf import settings

from fixtures.utils.general import get_file_path


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
    officials = models.ManyToManyField('CompetitionOfficial', blank=True)
    rules = models.ManyToManyField('RuleSet', blank=True)

    def __str__(self):
        return self.name


class Penalty(models.Model):
    description = models.CharField(max_length=400)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name_plural = "penalties"


class Rule(models.Model):
    number = models.IntegerField()
    penalty = models.ManyToManyField('Penalty', blank=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return self.ruleset_set.first().__str__() + " - " + self.number.__str__()


class RuleSet(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=50)
    rules = models.ManyToManyField('Rule', blank=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return self.name


class RuleParagraph(models.Model):
    number = models.IntegerField()
    content = models.CharField(max_length=500)
    rule = models.ForeignKey('Rule', on_delete=models.CASCADE)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return self.content


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
                                 null=True, blank=True)
    umpire_b = models.ForeignKey('Umpire',
                                 related_name='fixtures_as_umpire_b',
                                 on_delete=models.SET_NULL,
                                 null=True, blank=True)
    match_card_submission_url = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.date.__str__() + ' - ' + self.team_a.__str__() + " vs " + self.team_b.__str__()


class FixtureCancellation(models.Model):
    cancellation_reporter = models.ForeignKey('clubs.Member', on_delete=models.SET_NULL, null=True)
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    datetime_cancelled = models.DateTimeField()
    cancellation_reason = models.CharField(max_length=30)
    cancelled_by_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True)
    more_info = models.CharField(max_length=150)
    response = models.ForeignKey('CancellationResponse', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.fixture.__str__()


class CancellationResponse(models.Model):
    response = models.CharField(max_length=20)
    response_by = models.ForeignKey('fixtures.CompetitionOfficial', on_delete=models.SET_NULL, null=True)
    additional_comments = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)


class MatchCardImage(models.Model):
    image = models.FileField(upload_to=get_file_path, unique=True)
    name = models.CharField(max_length=50, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Official(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True


class MatchOfficial(Official):
    pass


class Umpire(MatchOfficial):
    pass


class CompetitionOfficial(Official):
    type = models.IntegerField()

    def __str__(self):
        return self.user.username
