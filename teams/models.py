from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=30)
    short_name = models.CharField(max_length=5, null=True)
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE)
    squad = models.ManyToManyField('clubs.Member', related_name='squads', blank=True)
    involved_in = models.ManyToManyField('fixtures.Competition', blank=True)

    def __str__(self):
        return self.club.name + " - " + self.short_name
