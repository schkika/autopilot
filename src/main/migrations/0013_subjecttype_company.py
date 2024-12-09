# Generated by Django 4.2.1 on 2023-05-26 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_alter_assosiate_profession'),
        ('main', '0012_alter_subject_scanned_documents'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjecttype',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.company', verbose_name='Kancelarija'),
        ),
    ]
