# Generated by Django 2.1.11 on 2019-11-17 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0035_rearrangementresponse_when'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cancellationresponse',
            name='additional_comments',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]