# Generated by Django 4.2.1 on 2023-05-29 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0012_alter_meettime_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meettime',
            name='start_time',
            field=models.TimeField(default='11:09'),
        ),
    ]
