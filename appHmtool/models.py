from django.db import models

# Create your models here.
class Transactions(models.Model):
    upload_time = models.DateTimeField(null=True)
    sale_warehouse = models.CharField(max_length=200, null=True)
    sale_id = models.CharField(max_length=200, null=True)
    sale_status = models.CharField(max_length=200, null=True)
    sale_updated_time = models.DateTimeField(null=True)
    sale_client = models.CharField(max_length=200, null=True)
    sale_name = models.CharField(max_length=200, null=True)
    product_barcode = models.CharField(max_length=200, null=True)
    product_name_cn = models.CharField(max_length=200, null=True)
    product_name_en = models.CharField(max_length=200, null=True)
    product_brand = models.CharField(max_length=200, null=True)
    product_supplier = models.CharField(max_length=200, null=True)
    sale_quantity = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    sale_price = models.DecimalField(max_digits=10,decimal_places=4,null=True)
    sale_payment = models.DecimalField(max_digits=10,decimal_places=4,null=True)
    upload_id = models.CharField(max_length=200, null=True)
