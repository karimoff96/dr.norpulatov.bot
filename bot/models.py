from django.db import models
from django.utils import timezone


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

class Patient(models.Model):
    LANGUAGE_CHOICES = (
        ("UZ", ("Кирилча")),
        ("uz", ("O'zbekcha")),
    )
    user_id = models.BigIntegerField()
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    username = models.CharField(max_length=128, blank=True)
    week_day = models.CharField(max_length=128, blank=True)
    checkup_time = models.DateTimeField(default=timezone.now)
    gender = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(default=0, blank=True)
    reason = models.TextField(blank=True)
    phone_number = models.CharField(max_length=128, blank=True)
    language = models.CharField(default="uz", choices=LANGUAGE_CHOICES, max_length=10)
    # doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    status = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.first_name
class Appointment(models.Model):
    pass