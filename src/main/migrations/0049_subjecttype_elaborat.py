# Generated by Django 4.2.3 on 2023-08-24 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_subject_responsible_worker'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjecttype',
            name='elaborat',
            field=models.BooleanField(default='False', verbose_name='Elaborat'),
            preserve_default=False,
        ),
    ]
