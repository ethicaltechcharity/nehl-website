# Generated by Django 2.1.11 on 2019-09-11 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0008_auto_20190909_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='clubmanagementposition',
            name='type',
            field=models.CharField(choices=[('CHAIR', 'Chair'), ('SECRETARY', 'Secretary')], default='CHAIR', max_length=30),
            preserve_default=False,
        ),
    ]