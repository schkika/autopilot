# Generated by Django 4.2.1 on 2023-05-26 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_alter_assosiate_profession'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='can_add_assosiate',
            field=models.BooleanField(default=False, verbose_name='Dodaje saradnike'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='can_add_user',
            field=models.BooleanField(default=False, verbose_name='Dodaje korisnike'),
        ),
    ]
