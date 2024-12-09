import datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="Puni naziv")
    short_name = models.CharField(max_length=255, verbose_name="Skraćeni naziv", blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name="Adresa", blank=True, null=True)
    zipp_code = models.CharField(max_length=255, verbose_name="Poštanski broj", blank=True, null=True)
    city = models.CharField(max_length=255, verbose_name="Mesto", blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True, verbose_name="region")
    department = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ispostava")
    telefon = models.CharField(max_length=255, blank=True, null=True, verbose_name="Telefon")
    email = models.CharField(max_length=255, blank=True, null=True, verbose_name="Email")
    id_number = models.CharField(max_length=255, verbose_name="Matični broj", blank=True,null=True)
    tax_number = models.CharField(max_length=255, verbose_name="Poreski broj",blank=True, null=True)
    account_number = models.CharField(max_length=255, verbose_name="Tekući račun", blank=True, null=True)
    type = models.CharField(max_length=255, verbose_name="Pravni oblik", blank=True, null=True)
    foundation_date = models.DateField(verbose_name="Datum osnivanja",blank=True, null=True)
    representative = models.CharField(max_length=255, verbose_name="Zastupnik", blank=True, null=True)
    activity = models.CharField(max_length=255, verbose_name="Delatnost", blank=True, null=True)
    grider_login_name = models.CharField(max_length=255, verbose_name="Grider login name", blank=True, null=True)
    grider_password = models.CharField(max_length=255, verbose_name="Grider password", blank=True, null=True)

    class Meta:
        verbose_name = 'Kancelarija'
        verbose_name_plural = 'Kancelarije'

    def __str__(self) -> str:
        return self.full_name


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="kacelarija")
    type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tip korisnika")
    licence_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Broj licence")
    education = models.CharField(max_length=255, blank=True, null=True, verbose_name="Obrazovanje")
    telefon_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Broj telefona")
    has_full_access = models.BooleanField(default=False, verbose_name='Administrator')
    can_open_subject = models.BooleanField(default=False, verbose_name='Otvara projekte')
    can_add_user = models.BooleanField(default=False, verbose_name='Dodaje korisnike')
    can_add_assosiate = models.BooleanField(default=False, verbose_name='Dodaje saradnike')
    can_add_client = models.BooleanField(default=False, verbose_name='Dodaje Stranke')


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Korisnik'
        verbose_name_plural = 'Korisnici'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class RegisterReq(models.Model):
    company_name = models.CharField(max_length=255, blank=False, null=False, verbose_name="Kancelarija")
    email = models.EmailField(unique=True, verbose_name="email")
    date = models.DateField(auto_now_add=True)
    class Meta:
        verbose_name = 'Zahtev za registraciju'
        verbose_name_plural = 'Zahtevi za registraciju'

    def __str__(self):
        return self.company_name
    

class Assosiate(models.Model):
    first_name = models.CharField(max_length=255, blank=False, null=False, verbose_name="Ime")
    last_name = models.CharField(max_length=255, blank=False, null=False, verbose_name="Prezime")
    email = models.EmailField(unique=True, verbose_name="email")
    profession = models.CharField(max_length=255, blank=True, null=True, verbose_name="Zanimanje")
    company = models.ManyToManyField(Company, verbose_name="kancelarija")
    user = models.OneToOneField(CustomUser, blank=True, null=True, on_delete=models.SET_NULL)
    class Meta:
        verbose_name = "Saradnik"
        verbose_name_plural = "Saradnici"

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    

class Client(models.Model):
    first_name = models.CharField(max_length=255, blank=False, null=False, verbose_name="Ime")
    last_name = models.CharField(max_length=255, blank=False, null=False, verbose_name="Prezime")
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mesto stanovanja stranke")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresa stranke")
    contact = models.CharField(max_length=255, blank=False, null=False, verbose_name="Kontakt stranke")
    email = models.EmailField(blank=True, null=True, verbose_name="email")
    company = models.ManyToManyField(Company, verbose_name="Kancelarija")
    user = models.OneToOneField(CustomUser, blank=True, null=True, on_delete=models.SET_NULL)
    class Meta:
        verbose_name = "Stranka"
        verbose_name_plural = "Stranke"

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    

class Modul(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, verbose_name="Ime modula")

    def __str__(self):
        return self.name
    

class Licence(models.Model):
    user = models.ForeignKey(CustomUser, blank=False, null=False, on_delete=models.CASCADE, verbose_name="Korisnik")
    modul = models.ForeignKey(Modul, blank=False, null=False, on_delete=models.CASCADE, verbose_name="Modul")
    pin = models.CharField(max_length=255, blank=True, null=True, verbose_name="PIN")
    valid = models.DateField(blank=False, null=False, default=datetime.date.today)
    server_time = models.FloatField(blank=True, null=True)