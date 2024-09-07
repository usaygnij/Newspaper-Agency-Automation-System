from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
# from django.db import models
from django.contrib.auth.models import AbstractUser
# from datetime import datetime
from django.utils import timezone
from django.core.validators import RegexValidator

a_numeric = RegexValidator(r'^[a-zA-Z]*$', 'only alphabets are allowed')
d_ten = RegexValidator(r'^[0-9]{10}$', 'enter 10 digits')
d_six = RegexValidator(r'^[0-9]{6}$', 'enter 6 digits')

class Distributors(models.Model):
    distributor_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    d_phone = models.CharField(max_length=200, validators=[d_ten])

class Publications(models.Model):
    paper_name = models.CharField(max_length=200, validators=[a_numeric])
    language = models.CharField(max_length=200, validators=[a_numeric])
    description = models.CharField(max_length=200)
    price = models.FloatField()

    def __str__(self):
        return self.paper_name

    class Meta:
        ordering = ('paper_name',)

class Customers(models.Model):
    customer_name = models.CharField(max_length=200, validators=[a_numeric])
    address = models.CharField(max_length=200)
    pincode = models.CharField(max_length=6, default='', validators=[d_six])
    phone = models.CharField(max_length=200, validators=[d_ten])
    subscription = models.ManyToManyField('Publications',default='')
    due = models.FloatField(default=0)

class Subscript(models.Model):
    phone = models.CharField(max_length=200)
    subscription = models.ManyToManyField('Publications',default='')

class WithHold(models.Model):
    customer_id = models.ForeignKey('Customers', on_delete=models.CASCADE)
    from_date = models.DateField(default=timezone.now)
    to_date = models.DateField(default=timezone.now)

class Summary(models.Model):
    distributor_id = models.ForeignKey('Distributors', on_delete=models.CASCADE)
    customer_id = models.ForeignKey('Customers', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)