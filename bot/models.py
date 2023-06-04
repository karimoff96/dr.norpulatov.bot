from django.db import models
from django.utils import timezone
from datetime import datetime
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from datetime import timedelta


class WeekDay(models.Model):
    weekdays = (
        ("Dushanba", "Dushanba"),
        ("Seshanba", "Seshanba"),
        ("Chorshanba", "Chorshanba"),
        ("Pashanba", "Pashanba"),
        ("Juma", "Juma"),
        ("Shanba", "Shanba"),
        ("Yakshanba", "Yakshanba"),
    )
    week_day = models.CharField(choices=weekdays, default=3, max_length=20, unique=True)

    def __str__(self) -> str:
        return f"{self.week_day}"


class Time(models.Model):
    start_time = models.TimeField(default=datetime.now().strftime("%H:%M"), unique=True)
    end_time = models.TimeField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return str(self.start_time)


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
        verbose_name_plural = "Doctors"
        indexes = [models.Index(fields=["first_name"])]


class DocWorkDay(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day = models.ForeignKey(WeekDay, on_delete=models.CASCADE)
    times = models.ManyToManyField(Time)
    active = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.doctor.first_name} {self.day.week_day}'
    
    def validate_unique(self, exclude=None):
        queryset = type(self).objects.filter(doctor=self.doctor, day=self.day)
        if self.pk is not None:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.exists():
            raise ValidationError(f"Doc work day with this Doctor and Day already exists. You better change the existing day`s times!")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'day'], name='unique_doctor_day')
        ]
        
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
    statuses = (
        ("applied", "Ariza topshirildi"),
        ("successfull", "Qabul yakunlandi"),
        ("cancel", "Bekor qilindi"),
        ("unsuccessfull", "Bajarilmadi"),
    )
    docworkday = models.ForeignKey(DocWorkDay, on_delete=models.CASCADE, blank=True, null=True)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    complaint = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    consultation_type = models.CharField(default="off", max_length=25)
    urgent = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    price = models.DecimalField(default=0, decimal_places=0, max_digits=8)
    card = models.CharField(max_length=250, blank=True)
    status = models.CharField(choices=statuses, default="applied", max_length=15)

    def __str__(self) -> str:
        return f"{self.patient.first_name} {self.patient.last_name}"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"


