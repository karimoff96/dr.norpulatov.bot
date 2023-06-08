from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Appointment, Doctor, DocWorkDay, Patient, Time, WeekDay

# Register your models here.
admin.site.unregister(Group)

admin.site.register(Time)


class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone_number",
        "created_at",
        "active",
        'source',
    ) 

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


admin.site.register(Patient, PatientAdmin)
admin.site.register(WeekDay)
admin.site.register(DocWorkDay)


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "complaint", "urgent", "created_at", "active")
    list_editable = ("active",)
    list_filter = ("urgent", "active", "created_at")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.order_by("-urgent", "-created_at")
        return queryset


admin.site.register(Appointment, AppointmentAdmin)
class DoctorAdmin(admin.ModelAdmin): # new
     readonly_fields = ['img_preview']
     list_display = ['first_name', 'img_preview']

admin.site.register(Doctor, DoctorAdmin)