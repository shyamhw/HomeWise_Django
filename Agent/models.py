from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import (
	BaseUserManager,
	AbstractBaseUser
)
from django.core.mail import (
	send_mail,
	BadHeaderError
)
from django.db import models
from django.utils import crypto

import logging

from smtplib import SMTPException

class VendorRegion(models.Model):
    # Classify MLS regions in vendor regions
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return "Vendor Region: " + self.name

class Tag(models.Model):
    # Tags describe Vendors and Steps
    name = models.CharField(max_length=150, null=True, blank=True, unique=True)
    def __str__(self):
        return 'Tag: ' + str(self.name)

class MLSRegion(models.Model):
    # Model MLS Region
    short_name = models.CharField(max_length=30, null=True, blank=True)
    long_name = models.CharField(max_length=100, null=True, blank=True)
    office_location = models.CharField(max_length=100, null=True, blank=True)
    vendor_region = models.ForeignKey(VendorRegion, on_delete=models.CASCADE)

class Role(models.Model):
    AGENT  = 1
    CLIENT = 2
    VENDOR = 3
    ROLE_CHOICES = (
        (AGENT, 'agent'),
        (CLIENT, 'client'),
        (VENDOR, 'vendor'),
    )

    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):
        return self.get_id_display()

class HomeWiseUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: creates a super user
        """
        u = self.create_user(email, password, **kwargs)
        u.is_staff = True
        u.is_active = True
        print("hi")
        u.save(using=self._db)
        return u

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
	email = models.EmailField(
		max_length = 254,
		unique = True
	)
	is_active 	= models.BooleanField(default=True)
	is_staff 	= models.BooleanField(default=False)
	is_admin	= models.BooleanField(default=False)

	first_name	= models.CharField(
		max_length=50,
		null=True,
		blank=True
	)
	last_name	= models.CharField(
		max_length=50,
		null=True,
		blank=True
	)

	temp_password = models.BooleanField(default=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = HomeWiseUserManager()

	def __str__(self):
		return str(self.email)

	def get_full_name(self):
		return str(self.first_name) + " " + str(self.last_name)

	def get_short_name(self):
		return str(self.email)

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	def reset_password(self):
		"""
		Reset password to generated temp password
		"""
		gen_password = crypto.get_random_string()
		logger = logging.getLogger('django')
		logger.setLevel(logging.DEBUG)
		try:
			send_mail("Reset Password - HomeWise", "Here is your newly generated temporary password: " + gen_password, settings.EMAIL_FROM_ADDRESS, [self.email])
		except SMTPException as e:
			logger.info("SendMail Error: " + str(e))
			return False
		self.set_password(gen_password)
		self.temp_password = True
		self.save()
		return True

class Agent(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    ##first_name = models.CharField(max_length=100, null=True, blank=True)
    ##last_name = models.CharField(max_length=100, null=True, blank=True)
    mls_region = models.CharField(max_length=254, null=True, blank=True)
    mls_id = models.CharField(max_length=100, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)

    class Meta:
        app_label = 'Agent'
        unique_together = (("mls_region", "mls_id"),)

    def __str__(self):
        return self.user.get_full_name() + " (" + self.user.email + ")"

class Client(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
     	null=True   
    )

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

    def __str__(self):
        return "[Agent] " + str(self.agent) + ", [Client] " + self.first_name + " " + self.last_name

    def getName(self):
        return str(self.last_name) + ", " + str(self.first_name)

class Step(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    ordering = models.IntegerField('ordering', null=True, blank=True)
    name = models.CharField(max_length=60, null=True, blank=True)
    complete = models.BooleanField(default=False)
    agent_email = models.CharField(max_length=254, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    class Meta:
        ordering = ('date',)

    def __str__(self):
        return "[Client] " + str(self.client.getName()) + " - " + self.name

class Vendor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
     	null=True   
    )
    # Metadata
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    company_name = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.CharField(max_length=254, null=True, blank=True)
    # Service info
    tags = models.ManyToManyField(Tag)
    long_description = models.CharField(max_length=300, null=True, blank=True)
    # Geographic info
    address = models.CharField(max_length=200, null=True, blank=True)
    vendor_region = models.ForeignKey(VendorRegion, on_delete=models.CASCADE)
    # Reputation info
    ##prev_clients = models.ManyToManyField(Agent)
    yelp_link = models.CharField(max_length=200, null=True, blank=True)
    facebook_link = models.CharField(max_length=200, null=True, blank=True)
    website_link = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        if self.company_name:
            return "Vendor: " + self.company_name
        return "Vendor: " + self.last_name + ", " + self.first_name
