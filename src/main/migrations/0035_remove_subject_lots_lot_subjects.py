# Generated by Django 4.2.3 on 2023-07-20 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_lot_lotobject_subject_lots'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='lots',
        ),
        migrations.AddField(
            model_name='lot',
            name='subjects',
            field=models.ManyToManyField(to='main.subject'),
        ),
    ]