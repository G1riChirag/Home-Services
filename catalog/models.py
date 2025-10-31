
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    base_price_cents = models.IntegerField(default=0)
    def __str__(self): return self.name

class ServicePackage(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    price_cents = models.IntegerField(default=0)
    photos = models.JSONField(default=list, blank=True)
    options = models.JSONField(default=dict, blank=True)
    is_customisable = models.BooleanField(default=False)
    def __str__(self): return self.title
