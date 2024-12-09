from django.contrib import admin
from django.forms import Textarea
from django.db import models
from .models import GpsDevice, SubjectType, Subject, Comment, Katastar, ElaboratDocument, ElaboratType, ElaboratSubjectDocument

admin.site.register(SubjectType)
admin.site.register(Comment)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'service_type', 'municipality')
    search_fields = ['id', 'company__full_name', 'service_type__name', 'municipality']

@admin.register(GpsDevice)
class GpsDeviceAdmin(admin.ModelAdmin):
    list_display = ('company', 'manufacturer', 'model', 'serial_number', 'certificate', 'valid_until', 'type')

@admin.register(ElaboratDocument)
class ElaboratDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'aws_name', 'template_number', 'root', 'grider', 'cad', 'content')

@admin.register(ElaboratType)
class ElaboratTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'document', 'order')
    search_fields = ['type__name', 'document__name']


@admin.register(ElaboratSubjectDocument)
class ElaboratSubjectDocumentAdmin(admin.ModelAdmin):
    list_display = ('elaborat', 'elaborat_subject', 'document')

    def elaborat_subject(self, obj):
        return obj.elaborat.subject.id
    
    elaborat_subject.short_description = 'Broj Predmeta'


@admin.register(Katastar)
class KatastarAdmin(admin.ModelAdmin):
    list_display = ('cadastral_municipality', 'municipality', 'office')
    search_fields = ('cadastral_municipality', 'municipality', 'office')