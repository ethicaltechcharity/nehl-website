# Generated by Django 2.1.11 on 2019-11-13 00:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0034_auto_20191113_0029'),
    ]

    operations = [
        migrations.AddField(
            model_name='rearrangementresponse',
            name='when',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]