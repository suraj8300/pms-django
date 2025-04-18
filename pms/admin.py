from django.contrib import admin
from .models import Drug, Prescription

admin.site.register(Drug)
admin.site.register(Prescription)