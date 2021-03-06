# Generated by Django 2.2.2 on 2019-08-24 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0009_competition_parent_competition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='parent_competition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_competition', to='fixtures.Competition'),
        ),
    ]
