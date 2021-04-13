from django.db import models

# Create your models here.
class covid(models.Model):
    iso_code = models.CharField(max_length=32)
    continent = models.CharField(max_length=32)
    location = models.CharField(max_length=32)
    date = models.DateField()
    total_cases = models.IntegerField(null=True)
    new_cases = models.IntegerField(null=True)
    new_cases_smoothed = models.FloatField(null=True)
    total_deaths = models.IntegerField(null=True)
    new_deaths = models.IntegerField(null=True)
    new_deaths_smoothed = models.FloatField(null=True)