from django.db import models

# pip install python-barcode==0.13.1
# Create your models here.
class BarCod(models.Model):
    name = models.IntegerField()
    barcode = models.ImageField(upload_to='', blank=True)
