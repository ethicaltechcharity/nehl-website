# Generated by Django 2.1.11 on 2019-10-25 23:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0016_club_dashboard_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='fixture_coordinator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fixture_coordinator_for', to='clubs.Member'),
        ),
        migrations.AlterField(
            model_name='club',
            name='main_contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='main_contact_for', to='clubs.Member'),
        ),
    ]