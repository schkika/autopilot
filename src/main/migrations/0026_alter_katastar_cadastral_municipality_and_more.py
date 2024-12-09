# Generated by Django 4.2.1 on 2023-06-14 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_alter_katastar_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='katastar',
            name='cadastral_municipality',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Katastarska opština'),
        ),
        migrations.AlterField(
            model_name='katastar',
            name='municipality',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Opština'),
        ),
    ]
