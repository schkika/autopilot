# Generated by Django 4.2.3 on 2023-08-03 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_alter_gpsdevice_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gpsdevice',
            name='blh',
        ),
        migrations.RemoveField(
            model_name='gpsdevice',
            name='enh',
        ),
        migrations.RemoveField(
            model_name='gpsdevice',
            name='xyz',
        ),
    ]