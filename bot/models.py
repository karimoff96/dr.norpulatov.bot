from django.db import models
import segno
from django.utils.html import mark_safe
import uuid
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

class Specialization(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Faoliyat turi"
        verbose_name_plural = "Faoliyat turlari"
        indexes = [models.Index(fields=["name"])]

class Doctor(TimeStampedModel, models.Model):
    doc_id = models.BigIntegerField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    about = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=128, blank=True)
    available = models.BooleanField(default=True)
    active = models.BooleanField(default=False)
    specialization = models.ManyToManyField(Specialization, related_name="doctor")
    image = models.ImageField(upload_to="doctor")
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
        verbose_name = "Shifokor"
        verbose_name_plural = "Shifokorlar"
        indexes = [models.Index(fields=["first_name"])]

    def qr(self):
        qrcode = segno.make(
            f"https://t.me/openai_chat_gpt_robot?start={self.doc_token}"
        )
        file_name = f"media/images/{self.doc_token}.png"
        qrcode.save(file_name, dark="darkred", light="lightblue", scale=10)
        return file_name


class Patient(TimeStampedModel, models.Model):
    src = (
        ("bot", "Bot orqali"),
        ("web", "Admin panel orqali"),
    )
    user_id = models.BigIntegerField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=256, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(default=0, blank=True)
    phone_number = models.CharField(max_length=128, blank=True)
    step = models.IntegerField(default=0, null=True, blank=True)
    language = models.CharField(default="uz", max_length=10)
    active = models.BooleanField(default=False)
    source = models.CharField(choices=src, default="web", max_length=15)

    def __str__(self) -> str:
        return f"{self.first_name}"

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"


class Appointment(TimeStampedModel, models.Model):
    TYPES = (
        ("bot", _("Bot orqali")),
        ("web", _("Admin panel orqali")),
    )
    doctor = models.ForeignKey(
        "Doctor",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=256, blank=True)
    phone_number = models.CharField(max_length=13, blank=True)
    app_date = models.DateField()
    app_time = models.TimeField()
    type = models.CharField(choices=TYPES, default="web", max_length=15)
    complaint = models.TextField(
        blank=True, verbose_name=_("Shikoyat, qo'shimcha ma'lumot")
    )
    active = models.BooleanField(default=False)
    urgent = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.doctor.first_name}-{self.name}-{self.app_date}"

    class Meta:
        verbose_name = "Shifokor ko'rigi"
        verbose_name_plural = "Shifokor ko'riklari"
        indexes = [models.Index(fields=["doctor"])]


class Letter(models.Model):
    count = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    message_id = models.BigIntegerField(default=0)
    admin_id = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
