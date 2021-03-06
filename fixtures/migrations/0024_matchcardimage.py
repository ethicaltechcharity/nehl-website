# Generated by Django 2.1.11 on 2019-09-20 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0023_fixture_match_card_submission_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchCardImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='match_cards')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
