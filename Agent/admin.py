from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Agent)
admin.site.register(models.Client)
admin.site.register(models.Step)