# Generated by Django 4.2.1 on 2023-05-31 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_customuser_can_add_client'),
        ('main', '0019_subject_client_alter_subject_client_city_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='client',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='client_address',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='client_city',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='client_contact',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='client_name',
        ),
        migrations.RemoveField(
            model_name='subjecttype',
            name='client_address',
        ),
        migrations.RemoveField(
            model_name='subjecttype',
            name='client_city',
        ),
        migrations.RemoveField(
            model_name='subjecttype',
            name='client_name',
        ),
        migrations.AddField(
            model_name='subject',
            name='clients',
            field=models.ManyToManyField(to='accounts.client'),
        ),
    ]
