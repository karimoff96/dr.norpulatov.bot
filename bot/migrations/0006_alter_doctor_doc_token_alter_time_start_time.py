# Generated by Django 4.2.1 on 2023-06-14 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_alter_doctor_doc_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='doc_token',
            field=models.CharField(default='be145731-7d28-4b77-9239-d5df0e28a922', max_length=256),
        ),
        migrations.AlterField(
            model_name='time',
            name='start_time',
            field=models.TimeField(default='16:17', unique=True),
        ),
    ]
