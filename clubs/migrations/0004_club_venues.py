# Generated by Django 2.2.2 on 2019-08-22 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0004_auto_20190822_1631'),
        ('clubs', '0003_auto_20190822_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='venues',
            field=models.ManyToManyField(through='fixtures.VenueUseType', to='fixtures.Venue'),
        ),
    ]