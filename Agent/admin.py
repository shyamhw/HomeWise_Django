from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
# Register your models here.
admin.site.register(models.Agent)
admin.site.register(models.Client)
admin.site.register(models.Step)
admin.site.register(models.VendorRegion)
admin.site.register(models.Tag)
admin.site.register(models.MLSRegion)
admin.site.register(models.Vendor)
admin.site.register(models.User, UserAdmin)