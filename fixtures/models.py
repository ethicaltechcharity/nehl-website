from django.db import models
from django.conf import settings

from fixtures.utils.general import get_file_path


class Season(models.Model):
    years = models.CharField(max_length=6)
    display_name = models.CharField(max_length=7)
    teams = models.ManyToManyField('teams.Team')
    competition = models.ForeignKey('fixtures.Competition', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.display_name + ' - ' + self.competition.__str__()


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
    config = models.ManyToManyField('CompetitionConfigItem', blank=True)
    current_season = models.OneToOneField('Season',
                                          on_delete=models.SET_NULL,
                                          related_name='competition_current',
                                          null=True, blank=True)

    def __str__(self):
        return self.name


class CompetitionConfigItem(models.Model):
    key = models.CharField(max_length=25)
    value = models.BooleanField()

    def __str__(self):
        return self.key + ': ' + self.value.__str__()


class LeagueStanding(models.Model):
    league = models.ForeignKey('Competition', on_delete=models.CASCADE)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    num_played = models.PositiveIntegerField(default=0)
    num_won = models.PositiveIntegerField(default=0)
    num_lost = models.PositiveIntegerField(default=0)
    num_drawn = models.PositiveIntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)


class Penalty(models.Model):
    description = models.CharField(max_length=400)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name_plural = 'penalties'


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
    result = models.OneToOneField('FixtureResult', on_delete=models.CASCADE, null=True, blank=True)
    metadata = models.OneToOneField('FixtureMetadata', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.date.__str__() + ' - ' + self.team_a.__str__() + " vs " + self.team_b.__str__()


class FixtureResult(models.Model):
    team_a_score = models.PositiveSmallIntegerField(default=0)
    team_b_score = models.PositiveSmallIntegerField(default=0)
    team_a_points = models.IntegerField(default=0)
    team_b_points = models.IntegerField(default=0)
    draw = models.BooleanField(default=False)
    winner = models.ForeignKey('teams.Team', related_name='wins', on_delete=models.SET_NULL, null=True, blank=True)
    loser = models.ForeignKey('teams.Team', related_name='losses', on_delete=models.SET_NULL, null=True, blank=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        if self.draw:
            return '{team_a} - {team_b} draw'.format(team_a=self.fixture.team_a, team_b=self.fixture.team_b)
        else:
            return '{winner} beat {loser}'.format(winner=self.winner, loser=self.loser)


def get_file_path(instance, filename):
    import uuid
    import os

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads/match_cards', filename)


class FixtureMetadata(models.Model):
    match_card_image = models.ImageField(upload_to=get_file_path, null=True)
    match_card_image_submitted = models.BooleanField(default=False)
    squad_a_selected = models.BooleanField(default=False)
    squad_b_selected = models.BooleanField(default=False)
    scorers_submitted = models.BooleanField(default=False)
    personal_penalties_submitted = models.BooleanField(default=False)
    start_time_submitted = models.BooleanField(default=False)

    time_match_card_image_submitted = models.DateTimeField(null=True)
    time_squad_a_selected = models.DateTimeField(null=True)
    time_squad_b_selected = models.DateTimeField(null=True)
    time_scorers_submitted = models.DateTimeField(null=True)
    time_penalties_submitted = models.DateTimeField(null=True)
    time_match_card_complete = models.DateTimeField(null=True)
    time_start_time_submitted = models.DateTimeField(null=True)

    umpire_a_signed = models.BooleanField(null=True)
    umpire_b_signed = models.BooleanField(null=True)
    captain_a_signed = models.BooleanField(null=True)
    captain_b_signed = models.BooleanField(null=True)

    issue_detected = models.BooleanField(default=False)


class MatchEvent(models.Model):
    time_occurred = models.DurationField(null=True, blank=True)
    appearance = models.ForeignKey('Appearance', on_delete=models.SET_NULL, null=True)
    fixture = models.ForeignKey('FixtureResult', on_delete=models.CASCADE)


class Goal(MatchEvent):
    pass


class PersonalPenalty(MatchEvent):
    awarded_by = models.ForeignKey('Umpire', on_delete=models.SET_NULL, null=True)
    penalty_type = models.ForeignKey('PersonalPenaltyType', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Personal penalties'


class PersonalPenaltyType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Player(models.Model):
    member = models.ForeignKey('clubs.Member', on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        if self.member is None:
            return self.first_name + ' ' + self.last_name
        else:
            return self.member.__str__()


class Appearance(models.Model):
    fixture = models.ForeignKey('Fixture', on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)

    def __str__(self):
        return self.team.__str__() + ': ' + self.player.__str__()


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
    additional_comments = models.CharField(max_length=1000, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)


class FixtureRearrangement(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    from_fixture = models.ForeignKey('fixtures.Fixture', on_delete=models.CASCADE, related_name='rearrangement_from')
    to_fixture = models.ForeignKey('fixtures.Fixture', on_delete=models.CASCADE, related_name='rearrangement_to')
    reason = models.CharField(max_length=150)


class RearrangementRequest(models.Model):
    original_fixture = models.ForeignKey('fixtures.Fixture', on_delete=models.CASCADE)
    new_date_time = models.DateTimeField()
    date_time_created = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=150)
    status = models.CharField(max_length=30)
    who_requested = models.ForeignKey('clubs.Member', on_delete=models.SET_NULL, null=True)


class RearrangementResponse(models.Model):
    answer = models.CharField(max_length=30)
    reason = models.CharField(max_length=150)
    request = models.ForeignKey('fixtures.RearrangementRequest', on_delete=models.CASCADE)
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    when = models.DateTimeField(auto_now_add=True)


class MatchCardImage(models.Model):
    image = models.FileField(upload_to=get_file_path, unique=True)
    name = models.CharField(max_length=50, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Official(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True


class MatchOfficial(Official):
    associated_club = models.ForeignKey('clubs.Club', on_delete=models.SET_NULL, null=True, blank=True)


class Umpire(MatchOfficial):
    identification_number = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.identification_number


class CompetitionOfficial(Official):
    type = models.IntegerField()

    def __str__(self):
        return self.user.username
