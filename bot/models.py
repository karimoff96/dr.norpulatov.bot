from typing import Any
from django.db import models
from django.utils import timezone
from datetime import datetime
from django.db.models.signals import post_save

# class Doctor(models.Model):
#     first_name = models.CharField(max_length=128, blank=True)
#     last_name = models.CharField(max_length=128, blank=True)
#     about = models.TextField(blank=True, null=True)
#     phone_number = models.CharField(max_length=128, blank=True)
#     available = models.BooleanField(default=True)
#     created_at = models.DateField(auto_now_add=True)
#     updated_at = models.DateField(auto_now=True)
#     active = models.BooleanField(default=True)

#     def __str__(self) -> str:
#         return self.first_name

#     class Meta:
#         verbose_name = "Doctor"
#         verbose_name_plural = "Doctors"
#         indexes = [models.Index(fields=["first_name"])]




class Patient(models.Model):
    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=256, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
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
    complaint = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    consultation_type = models.CharField(default="off", max_length=25)
    urgent=models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.patient.first_name} {self.patient.last_name}"
    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

# class MeetTime(models.Model):
#     week_day = models.DateField(default=timezone.now)
#     start_time = models.TimeField(default=datetime.now().strftime("%H:%M:%S"))
#     end_time = models.TimeField(default=datetime.now().strftime("%H:%M:%S"))
#     created_at = models.DateField(auto_now_add=True)
#     updated_at = models.DateField(auto_now=True)
#     active = models.BooleanField(default=True)






