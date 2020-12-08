from django.db import models

# Create your models here.
class delivery(models.Model):
    category = models.ForeignKey('dash.material', null=True, on_delete=models.DO_NOTHING)
    driverName = models.CharField(max_length=32, null=True)
    date = models.DateField()
    imgInfo = models.CharField(max_length=255, null=True)
    location = models.CharField(max_length=32)
    nickName = models.CharField(max_length=32, null=True)
    plateNumber = models.CharField(max_length=32)
    project = models.CharField(max_length=32)
    quantity = models.FloatField()
    receiveID = models.CharField(max_length=32)
    receiverName = models.CharField(max_length=32)
    time = models.TimeField()
    unit = models.CharField(max_length=32)
    uploadTime = models.DateTimeField()


class material(models.Model):
    categoryName = models.CharField(max_length=32)
    mainCategory = models.CharField(max_length=32)