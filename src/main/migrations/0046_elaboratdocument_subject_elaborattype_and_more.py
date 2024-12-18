# Generated by Django 4.2.3 on 2023-08-22 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_alter_elaboratdocument_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='elaboratdocument',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.subject', verbose_name='Predmet'),
        ),
        migrations.CreateModel(
            name='ElaboratType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.elaboratdocument', verbose_name='Dokument')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.subjecttype', verbose_name='Tip posla')),
            ],
            options={
                'verbose_name': 'Tip elaborata',
                'verbose_name_plural': 'Tipovi elaborata',
            },
        ),
        migrations.CreateModel(
            name='ElaboratSubjectDocuments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.elaboratdocument', verbose_name='Dokument')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.subject', verbose_name='Predmet')),
            ],
            options={
                'verbose_name': 'Dokument predmeta',
                'verbose_name_plural': 'Dokumenti predmeta',
            },
        ),
    ]
