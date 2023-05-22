from django.db import models
from django.utils import timezone


class Doctor(models.Model):
    first_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=128, null=True, blank=True)
    available = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)


# Create your models here.
class Patient(models.Model):
    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    username = models.CharField(max_length=128, null=True, blank=True)
    week_day = models.CharField(max_length=128, blank=True, null=True)
    checkup_time = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=128, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=False)
