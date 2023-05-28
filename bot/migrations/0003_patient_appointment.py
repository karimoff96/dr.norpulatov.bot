# Generated by Django 4.2.1 on 2023-05-28 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_remove_patient_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='appointment',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='bot.appointment'),
            preserve_default=False,
        ),
    ]
