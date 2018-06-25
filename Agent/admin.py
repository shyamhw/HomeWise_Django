from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Agent)
admin.site.register(models.Client)
admin.site.register(models.Step)
admin.site.register(models.VendorRegion)
admin.site.register(models.Tag)
admin.site.register(models.MLSRegion)
admin.site.register(models.Vendor)