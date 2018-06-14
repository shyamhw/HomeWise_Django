from django.db import models

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager

from django.utils import crypto

from django.conf import settings
from datetime import datetime

from django.core.mail import BadHeaderError, send_mail

from . import manager

import logging

from smtplib import SMTPException

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
    birthday = models.DateField(null=True, blank=True)

    temp_password = models.BooleanField(default=False)

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

    def reset_password(self):
        """
        Reset password to generated temp password
        """

        gen_password = crypto.get_random_string()
        print("New password: " + gen_password)
        logger = logging.getLogger('django')
        logger.setLevel(logging.DEBUG)
        try:
            send_mail("Reset Password - HomeWise", "Here is your newly generated temporary password: " + gen_password, settings.EMAIL_FROM_ADDRESS, [self.email])
            logger.info("SendMail successful!")
        except SMTPException as e:
            logger.info("SendMail Error: " + str(e))
            return False
        self.set_password(gen_password)
        self.temp_password = True
        self.save()
        print(self.password)

        return True

    def set_new_password(self, new_password):
        """
        Set password to new password
        """

        self.set_password(new_password)

        ## Clear temporary password status
        self.temp_password = False

        ## Save user model
        self.save()

        ## TODO: Revoke all issued OAuth2 Tokens

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
    commission_val = models.FloatField('commission val', max_length=20, blank=True, null=True)
    total_steps = models.IntegerField('total steps', null=True, blank=True)
    steps_complete = models.IntegerField('steps complete', null=True, blank=True)
    steps_percentage = models.FloatField('steps_percentage', max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

class Step(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    ordering = models.IntegerField('ordering', null=True, blank=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    complete = models.BooleanField(default=False)
    agent_email = models.CharField(max_length=254, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ('date',)

