from django.contrib import admin
from .models import Patient, Doctor
from django.contrib.auth.models import Group

# Register your models here.
admin.site.unregister(Group)
admin.site.register(Patient)
admin.site.register(Doctor)


class PatientModelAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "phone_number"]
