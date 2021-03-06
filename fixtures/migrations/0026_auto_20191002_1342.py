# Generated by Django 2.1.11 on 2019-10-02 12:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0015_auto_20190930_1700'),
        ('fixtures', '0025_auto_20190930_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='fixturecancellation',
            name='cancelled_by_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clubs.Club'),
        ),
        migrations.AlterField(
            model_name='competitionofficial',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='matchofficial',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
