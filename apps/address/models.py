from django.db import models


class Address(models.Model):
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    building = models.CharField(max_length=100)
    office = models.CharField(max_length=100)
