# Generated by Django 4.2.3 on 2023-08-24 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_alter_elaboratsubjectdocument_document_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='elaboratdocument',
            name='aws_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Naziv na AWS-u'),
        ),
    ]