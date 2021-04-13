from django.db import models


# Create your models here.
class Products(models.Model): 
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True)
    name_en = models.CharField(max_length=200, null=True)
    
class Company(models.Model):
    name = models.CharField(max_length=200, null=True)
    
class Transactions(models.Model):
    payment = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    price = models.DecimalField(max_digits=10,decimal_places=2, null=True)
    quantity = models.IntegerField(null=True)
    product = models.ForeignKey('Products', on_delete=models.SET_NULL, null=True)
    channel = models.CharField(max_length=200, null=True)
    time = models.DateTimeField(null=True)
    t_code = models.CharField(max_length=200, null=True)