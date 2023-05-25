from django.contrib import admin
from .models import Patient, Doctor, MeetTime, Appointment
from django.contrib.auth.models import Group

# Register your models here.
admin.site.unregister(Group)
admin.site.register(Patient)
admin.site.register(MeetTime)
admin.site.register(Doctor)
admin.site.register(Appointment)


class PatientModelAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "phone_number"]
