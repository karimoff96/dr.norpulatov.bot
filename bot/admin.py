from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Appointment, Doctor, Letter, Patient, Specialization

# Register your models here.
admin.site.unregister(Group)


class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone_number",
        "active",
        "source",
    )
    search_fields = ("first_name", "last_name")
    list_filter = ("first_name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


admin.site.register(Patient, PatientAdmin)


class LetterAdmin(admin.ModelAdmin):
    list_display = ["id", "message_id"]


admin.site.register(Letter, LetterAdmin)


class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone_number",
        "about",
        "image",
        "created",
        "modified",
    )
    list_display_links = ("last_name", "first_name")


class SpecializationAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


admin.site.register(Specialization, SpecializationAdmin)
admin.site.register(Doctor, DoctorAdmin)


from django.contrib import admin

from .models import Appointment


class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "doctor",
        "patient",
        "name",
        "app_date",
        "app_time",
        "type",
        "created",
        "modified",
        "complaint",
        "active",
        "urgent"
    )
    list_display_links = ("doctor", "patient", "name")


admin.site.register(Appointment, AppointmentAdmin)
