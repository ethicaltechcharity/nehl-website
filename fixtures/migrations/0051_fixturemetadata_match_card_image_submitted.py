# Generated by Django 3.0.3 on 2020-08-24 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0050_auto_20200823_2209'),
    ]

    operations = [
        migrations.AddField(
            model_name='fixturemetadata',
            name='match_card_image_submitted',
            field=models.BooleanField(default=False),
        ),
    ]