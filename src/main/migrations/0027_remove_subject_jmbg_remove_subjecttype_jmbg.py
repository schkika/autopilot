# Generated by Django 4.2.1 on 2023-06-15 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_alter_katastar_cadastral_municipality_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='jmbg',
        ),
        migrations.RemoveField(
            model_name='subjecttype',
            name='jmbg',
        ),
    ]