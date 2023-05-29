from django.db import models
from django.utils import timezone
from datetime import datetime
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from datetime import timedelta

class MeetTime(models.Model):
    weekdays = (
        ("du", "Dushanba"),
        ("se", "Seshanba"),
        ("ch", "Chorshanba"),
        ("pa", "Pashanba"),
        ("ju", "Juma"),
        ("sh", "Shanba"),
        ("ya", "Yakshanba"),
    )
    week_day = models.CharField(choices=weekdays, blank=True, default=3, max_length=10)
    start_time = models.TimeField(default=datetime.now().strftime("%H:%M"))
    end_time = models.TimeField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

    # class Meta:
    #     unique_together = ['doctor', 'start_time']

    # def clean(self):
    #     if self.pk:
    #         # Retrieve the previous MeetTime object for the same doctor
    #         previous_meet_time = MeetTime.objects.filter(doctor=self.doctor).exclude(pk=self.pk).last()
    #         if previous_meet_time:
    #             # Convert previous start time to datetime for addition
    #             previous_start_datetime = datetime.combine(datetime.now().date(), previous_meet_time.start_time)
    #             # Calculate the minimum start time for the next appointment
    #             minimum_start_datetime = previous_start_datetime + timedelta(minutes=30)
    #             minimum_start_time = minimum_start_datetime.time()
    #             if self.start_time < minimum_start_time:
    #                 raise ValidationError("Start time must be at least 30 minutes later than the previous time.")

    # def save(self, *args, **kwargs):
    #     self.clean()
    #     super().save(*args, **kwargs)

class Doctor(models.Model):
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    about = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=128, blank=True)
    availabe_times = models.ManyToManyField(MeetTime)
    available = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.first_name
    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
        indexes = [models.Index(fields=["first_name"])]


class Patient(models.Model):
    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=256, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    responsible_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(default=0, blank=True)
    phone_number = models.CharField(max_length=128, blank=True)
    step = models.IntegerField(default=0, null=True, blank=True)
    language = models.CharField(default="uz", max_length=10)
    active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.first_name}"

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    complaint = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    consultation_type = models.CharField(default="off", max_length=25)
    urgent = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    price = models.DecimalField(default=0, decimal_places=0, max_digits=8)
    card = models.CharField(max_length=250, blank=True)

    def __str__(self) -> str:
        return f"{self.patient.first_name} {self.patient.last_name}"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
