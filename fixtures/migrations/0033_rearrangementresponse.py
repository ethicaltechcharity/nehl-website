# Generated by Django 2.1.11 on 2019-11-13 00:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fixtures', '0032_fixturerearrangement_rearrangementrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='RearrangementResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_type', models.CharField(max_length=30)),
                ('reason', models.CharField(max_length=150)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fixtures.RearrangementRequest')),
                ('responder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
