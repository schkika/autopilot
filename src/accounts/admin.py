from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from autopilothome.helpers import email
from autopilothome.aws_utils import create_s3_bucket
from .models import CustomUser, Company, Licence, Modul, RegisterReq, Assosiate, Client

@admin.action(description="Registruj označene zahteve")
def register_requests(modeladmin, request, queryset):
    for obj in queryset:
        if Company.objects.filter(full_name=obj.company_name):
            email('Neuspešno registrovanje', 'Kancelarija sa ovim imenom registrovana', obj.email)
            obj.delete()
            continue
        # Allredy done in forms
        if CustomUser.objects.filter(email=obj.email):
            email('Neuspešno registrovanje', 'Korisnik sa ovim email-om registrovan', obj.email)
            continue
        new_company = Company.objects.create(full_name=obj.company_name)
        user = CustomUser.objects.create(email=obj.email)
        user.set_password('privremena')
        user.has_full_access = True
        user.type = 'employee'
        user.company = new_company
        new_company.save()
        user.save()
        email('Uspešno registrovanje na Autopilot platformu', 'Hvala što ste se registrovali, sada se možete prijaviti sa vašim emailom. Pri prvom prijavljivanju promenite šifru.', obj.email )
        create_s3_bucket(f'autopilot-kancelarija-{new_company.id}')
        obj.delete()



admin.site.unregister(Group)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name')

@admin.register(RegisterReq)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'date')
    actions = [register_requests]

@admin.register(CustomUser)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'company', 'type')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'company', 'has_full_access'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'company', 'has_full_access', 'type')
    search_fields = ('email', 'first_name', 'last_name')
    list_display_links = ('email', 'company',)
    ordering = ('email',)

@admin.register(Assosiate)
class AssosiateAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'profession')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'address')


@admin.register(Modul)
class ModulAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Licence)
class LicenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'modul', 'pin', 'valid', 'server_time')

    def user_email(self, obj):
        return obj.user.email
    
    user_email.short_description = 'Email'