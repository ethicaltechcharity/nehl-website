from django.db import models
from django.conf import settings


class Club(models.Model):
    name = models.CharField(max_length=30)
    short_name = models.CharField(max_length=6, null=True)
    primary_colour = models.CharField(max_length=7)
    secondary_colour = models.CharField(max_length=7)
    venues = models.ManyToManyField('fixtures.Venue',
                                    through='fixtures.VenueUseType')
    main_venue = models.ForeignKey('fixtures.Venue',
                                   on_delete=models.SET_NULL,
                                   related_name='main_club',
                                   null=True)

    def __str__(self):
        return self.name


class Member(models.Model):
    date_of_birth = models.DateField()
    registration_date = models.DateField()
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, related_name='members')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username
