from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
import segno
from django.utils.html import mark_safe
import uuid

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return str(self.start_time)


class Doctor(models.Model):
    doc_id = models.BigIntegerField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    about = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=128, blank=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    qrcode = models.CharField(max_length=100, blank=True)
    doc_token = models.CharField(max_length=256, default=str(uuid.uuid4()))
    show_img_preview = models.BooleanField(default=True)

    def img_preview(self): 
        if self.show_img_preview:
            return mark_safe(
                '<img src = "{url}" width = "200"/>'.format(url=f"/{self.qrcode}")
            )
        return ""

    def __str__(self) -> str:
        return self.first_name

    def save(self, *args, **kwargs) -> None:
        self.qrcode = self.qr()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
        indexes = [models.Index(fields=["first_name"])]

    def qr(self):
        qrcode = segno.make(
            f"https://t.me/openai_chat_gpt_robot?start={self.doc_token}"
        )
        file_name = f"media/images/{self.doc_token}.png"
        qrcode.save(file_name, dark="darkred", light="lightblue", scale=10)
        return file_name


class DocWorkDay(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day = models.ForeignKey(WeekDay, on_delete=models.CASCADE)
    times = models.ManyToManyField(Time)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.doctor.first_name} {self.day.week_day}"

    def validate_unique(self, exclude=None):
        queryset = type(self).objects.filter(doctor=self.doctor, day=self.day)
        if self.pk is not None:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.exists():
            raise ValidationError(
                f"Doc work day with this Doctor and Day already exists. Change the existing day`s times instead!"
            )
    def clean(self):
       if  len(self.doctor) == 0 or len(self.day)==0:
           
           raise ValidationError(
               {'doctor': "Doktorni tanlang", 'day': "Kunni tanlang"})
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["doctor", "day"], name="unique_doctor_day")
        ]


class Patient(models.Model):
    src = (
        ("bot", "Bot orqali"),
        ("web", "Admin panel orqali"),
    )
    user_id = models.BigIntegerField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(default=0, blank=True)
    phone_number = models.CharField(max_length=128, blank=True)
    step = models.IntegerField(default=0, null=True, blank=True)
    language = models.CharField(default="uz", max_length=10)
    active = models.BooleanField(default=False)
    source = models.CharField(choices=src, default="web", max_length=15)
    time = models.TimeField(null=True, blank=True)

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
    types = (
        ("bot", "Bot orqali"),
        ("web", "Admin panel orqali"),
    )
    docworkday = models.ForeignKey(
        DocWorkDay, on_delete=models.CASCADE, blank=True, null=True
    )
    time = models.ForeignKey(Time, on_delete=models.CASCADE, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    complaint = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    consultation_type = models.CharField(default="off", max_length=25)
    urgent = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    price = models.DecimalField(default=0, decimal_places=0, max_digits=8)
    card = models.CharField(max_length=250, blank=True)
    status = models.CharField(choices=statuses, default="applied", max_length=15)
    type = models.CharField(choices=types, default="web", max_length=15)

    def __str__(self) -> str:
        return f"{self.patient.first_name} {self.patient.last_name}"

    def validate_unique(self, exclude=None):
        queryset = type(self).objects.filter(
            docworkday=self.docworkday,
            time=self.time,
        )
        if self.pk is not None:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.exists():
            raise ValidationError(
                f"An appointment with the same doctor, day, and time already exists!"
            )
        super().validate_unique(exclude)

    @property
    def created(self):
        return (self.created_at + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")

    @property
    def created_date(self):
        return (self.created_at + timedelta(hours=5)).strftime("%Y-%m-%d")

    @property
    def updated(self):
        return (self.updated_at + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

    def save(self, *args, **kwargs):
        if self.type == "web":
            from .signals import send_appointment_to_doctor

            doc = Doctor.objects.filter(doc_id=self.docworkday.doctor.doc_id).first()
            data = {
                "id": len(Appointment.objects.filter(docworkday__doctor=doc)),
                "patient": {
                    "first_name": self.patient,
                    "last_name": self.patient.last_name,
                    "age": self.patient.age,
                    "complaint": self.complaint,
                },
                "appointment": {
                    "day": self.docworkday.day,
                    "time": self.time,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                },
            }
            send_appointment_to_doctor(data, self.docworkday.doctor.doc_id)
        super().save(*args, **kwargs)

class Letter(models.Model):
    count = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    message_id = models.BigIntegerField(default=0)
    admin_id = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
