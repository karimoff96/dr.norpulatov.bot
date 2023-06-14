from django import forms
from .models import Appointment, DocWorkDay


class AppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        docworkday = self.initial.get('docworkday')
        if docworkday:
            booked_times = Appointment.objects.filter(docworkday=docworkday).values_list('time_id', flat=True)
            self.fields['time'].queryset = self.fields['time'].queryset.exclude(id__in=booked_times)

    class Meta:
        model = Appointment
        fields = '__all__'