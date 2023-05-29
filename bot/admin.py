from django.contrib import admin
from .models import Patient, Appointment, Doctor, MeetTime
from django.contrib.auth.models import Group

# Register your models here.
admin.site.unregister(Group)


class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name','phone_number', 'created_at', 'active')  # Specify the fields to display in the list view

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # queryset = queryset.filter(active=True)  # Filter the queryset to include only active patients
        return queryset

admin.site.register(Patient, PatientAdmin)
admin.site.register(Doctor)
class MeetTimeAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'week_day', 'start_time','active')
    
admin.site.register(MeetTime)


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'complaint', 'urgent', 'created_at', 'active')
    list_editable = ('active',)
    list_filter = ('urgent', 'active', 'created_at')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # queryset = queryset.filter(active=True)
        queryset = queryset.order_by('-urgent', '-created_at')
        return queryset

admin.site.register(Appointment, AppointmentAdmin)