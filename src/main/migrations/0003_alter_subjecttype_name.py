# Generated by Django 4.2.1 on 2023-05-25 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_subjecttype_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjecttype',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Tip posla'),
        ),
    ]
