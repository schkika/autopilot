# Generated by Django 4.2.3 on 2023-08-25 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_remove_elaboratdocument_uploaded_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='elaboratdocument',
            name='template_number',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Broj obrasca'),
        ),
    ]