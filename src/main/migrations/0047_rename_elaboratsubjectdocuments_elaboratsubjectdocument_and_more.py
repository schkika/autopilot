# Generated by Django 4.2.3 on 2023-08-22 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_elaboratdocument_subject_elaborattype_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ElaboratSubjectDocuments',
            new_name='ElaboratSubjectDocument',
        ),
        migrations.AlterField(
            model_name='elaboratdocument',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Naziv dokumenta'),
        ),
    ]
