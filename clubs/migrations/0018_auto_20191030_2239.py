# Generated by Django 2.1.11 on 2019-10-30 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0017_auto_20191026_0003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='dashboard_link',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
