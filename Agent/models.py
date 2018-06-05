from django.db import models

from django.contrib.auth.models import AbstractBaseUser

from django.conf import settings
from datetime import datetime

from . import manager

# Create your models here.
class Agent(AbstractBaseUser):
    email = models.CharField(max_length=254, unique=True)
    username = models.CharField(max_length=254, unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    last_login = models.DateField(blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)

    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    mls_region = models.CharField(max_length=254, null=True, blank=True)
    mls_id = models.CharField(max_length=100, null=True, blank=True)

    objects = manager.CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        app_label = 'Agent'
        unique_together = (("mls_region", "mls_id"),)

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        return self.first_name
    def has_perm(self, perm, obj=None):
        """
        Dummy compulsory method as the base class is AbstractBaseUser
        """
        return True

    def has_module_perms(self, app_label):
        """
        Dummy compulsory method as the base class is AbstractBaseUser
        """
        return True


class Client(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    email = models.CharField(max_length=254, unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    client_type = models.CharField(max_length=1, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zipcode = models.CharField(max_length=5, null=True, blank=True)
    est_price = models.FloatField('est price', max_length=20, blank=True, null=True)
    commission = models.FloatField('commission', max_length=3, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

class Step(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    ordering = models.IntegerField('ordering', null=True, blank=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    complete = models.BooleanField(default=False)
    date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ('ordering',)


