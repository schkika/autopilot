# Generated by Django 4.2.3 on 2023-08-24 08:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_alter_elaborat_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elaborat',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.subject', verbose_name='Predmet'),
        ),
    ]
