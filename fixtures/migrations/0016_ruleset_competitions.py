# Generated by Django 2.1.1 on 2019-09-07 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0015_auto_20190907_2330'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruleset',
            name='competitions',
            field=models.ManyToManyField(blank=True, null=True, to='fixtures.Competition'),
        ),
    ]
