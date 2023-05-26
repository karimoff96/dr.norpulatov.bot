from django.db import models
from django.utils import timezone
from datetime import date, datetime


class Doctor(models.Model):
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    about = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=128, blank=True)
    available = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.first_name

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctor"
        indexes = [models.Index(fields=["first_name"])]


class Patient(models.Model):
    LANGUAGE_CHOICES = (
        ("UZ", ("Кирилча")),
        ("uz", ("O'zbekcha")),
    )
    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    username = models.CharField(max_length=128, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(default=0, blank=True)
    reason = models.TextField(blank=True)
    phone_number = models.CharField(max_length=128, blank=True)
    step = models.IntegerField(default=0, null=True, blank=True)
    language = models.CharField(default="uz", choices=LANGUAGE_CHOICES, max_length=10)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    urgent = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    def __str__(self) -> str:
        if len(self.first_name) > 0:
            return self.first_name
        else:
            return self.user_id

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        indexes = [models.Index(fields=["user_id"])]


class MeetTime(models.Model):
    week_day = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=datetime.now().strftime("%H:%M:%S"))
    end_time = models.TimeField(default=datetime.now().strftime("%H:%M:%S"))
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)


class Appointment(models.Model):
    TYPE = (
        ("on", ("online")),
        ("off", ("offline")),
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    consultation_type = models.CharField(choices=TYPE, default="off", max_length=25)
    meetup = models.ForeignKey(
        MeetTime, on_delete=models.CASCADE, null=True, blank=True
    )
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
