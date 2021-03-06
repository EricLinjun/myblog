# Generated by Django 3.1.2 on 2021-02-17 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covidDash', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='covid',
            name='new_cases',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='covid',
            name='new_cases_smoothed',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='covid',
            name='new_deaths',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='covid',
            name='new_deaths_smoothed',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='covid',
            name='total_cases',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='covid',
            name='total_deaths',
            field=models.IntegerField(null=True),
        ),
    ]
