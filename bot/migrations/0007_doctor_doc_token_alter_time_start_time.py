# Generated by Django 4.2.1 on 2023-06-08 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_alter_doctor_qrcode_alter_time_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='doc_token',
            field=models.CharField(default='e98ba724-2a11-4117-b9ae-981fd66b1039', max_length=256),
        ),
        migrations.AlterField(
            model_name='time',
            name='start_time',
            field=models.TimeField(default='16:00', unique=True),
        ),
    ]
