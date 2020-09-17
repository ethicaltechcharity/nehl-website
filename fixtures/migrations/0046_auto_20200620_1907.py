# Generated by Django 3.0.3 on 2020-06-20 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0045_auto_20200620_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalPenaltyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='personalpenalty',
            name='penalty_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fixtures.PersonalPenaltyType'),
        ),
    ]
