# Generated by Django 2.2.2 on 2019-09-01 21:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0012_venue_street_name'),
        ('clubs', '0005_club_short_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='main_venue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='main_club', to='fixtures.Venue'),
        ),
    ]