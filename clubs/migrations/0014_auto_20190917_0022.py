# Generated by Django 2.1.11 on 2019-09-16 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0013_auto_20190914_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transferrequest',
            name='evidence',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]
