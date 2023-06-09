# Generated by Django 4.2.1 on 2023-06-16 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0011_alter_doctor_doc_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='doc_token',
            field=models.CharField(default='55b2acb0-8a7e-4196-b7c6-5608f7f4e1ee', max_length=256),
        ),
        migrations.AlterField(
            model_name='letter',
            name='count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='letter',
            name='current',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='letter',
            name='message_id',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='time',
            name='start_time',
            field=models.TimeField(default='17:14', unique=True),
        ),
    ]
