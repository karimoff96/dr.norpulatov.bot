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
        "source",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


admin.site.register(Patient, PatientAdmin)
admin.site.register(WeekDay)
admin.site.register(DocWorkDay)


from django.contrib import admin
from .forms import AppointmentForm
from .models import Appointment, DocWorkDay


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "complaint", "urgent", "created_at", "active", 'time', 'docworkday')
    list_editable = ("active",)
    list_filter = ("urgent", "active", "created_at")
admin.site.register(Appointment, AppointmentAdmin)


