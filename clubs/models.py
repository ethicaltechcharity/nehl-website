from django.db import models
from django.conf import settings

POSITION_TYPE_CHOICES = [
    ('CHAIR', 'Chair'),
    ('SECRETARY', 'Secretary')
]


class Club(models.Model):
    name = models.CharField(max_length=60)
    short_name = models.CharField(max_length=12, null=True)
    primary_colour = models.CharField(max_length=7)
    secondary_colour = models.CharField(max_length=7)
    venues = models.ManyToManyField('fixtures.Venue',
                                    through='fixtures.VenueUseType')
    main_venue = models.ForeignKey('fixtures.Venue',
                                   on_delete=models.SET_NULL,
                                   related_name='main_club',
                                   null=True)
    management = models.ManyToManyField('Member',
                                        related_name='management_position',
                                        through='ClubManagementPosition')

    def __str__(self):
        return self.name


class ClubManagementPosition(models.Model):
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    holder = models.ForeignKey('Member', on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=POSITION_TYPE_CHOICES)

    def __str__(self):
        return self.club.name + " - " + self.holder.__str__()


class Member(models.Model):
    date_of_birth = models.DateField()
    registration_date = models.DateField()
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, related_name='members')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username


class TransferRequest(models.Model):
    datetime_submitted = models.DateTimeField()
    submitter = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    transfer_to = models.ForeignKey(
        Club, on_delete=models.SET_NULL, null=True, related_name='transfers_to')
    transfer_from = models.ForeignKey(
        Club, on_delete=models.SET_NULL, null=True, related_name='transfers_from')
    evidence = models.FileField()
