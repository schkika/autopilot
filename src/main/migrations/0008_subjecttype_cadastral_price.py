# Generated by Django 4.2.1 on 2023-05-25 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_subjecttype_lot_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjecttype',
            name='cadastral_price',
            field=models.BooleanField(default=False, verbose_name='Trošak katastra'),
            preserve_default=False,
        ),
    ]
