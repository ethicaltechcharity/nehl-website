# Generated by Django 3.0.3 on 2020-07-17 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0047_auto_20200620_2014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fixturemetadata',
            name='match_card_image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='fixturemetadata',
            name='personal_penalties_submitted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='fixturemetadata',
            name='scorers_submitted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='fixturemetadata',
            name='squad_a_selected',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='fixturemetadata',
            name='squad_b_selected',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='leaguestanding',
            name='goal_difference',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='leaguestanding',
            name='num_drawn',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='leaguestanding',
            name='num_lost',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='leaguestanding',
            name='num_played',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='leaguestanding',
            name='num_won',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='leaguestanding',
            name='total_points',
            field=models.IntegerField(default=0),
        ),
    ]