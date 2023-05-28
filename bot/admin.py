from django.contrib import admin
from .models import Patient, Appointment
from django.contrib.auth.models import Group

# Register your models here.
admin.site.unregister(Group)


class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name','phone_number', 'created_at', 'active')  # Specify the fields to display in the list view

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(active=True)  # Filter the queryset to include only active patients
        return queryset

admin.site.register(Patient, PatientAdmin)


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'complaint', 'urgent', 'created_at')
    list_filter = ('urgent',)
    ordering = ('urgent', '-created_at')

admin.site.register(Appointment, AppointmentAdmin)