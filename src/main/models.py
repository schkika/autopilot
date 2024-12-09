from django.db import models
from accounts.models import CustomUser, Assosiate, Company, Client


class SubjectType (models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, verbose_name="Tip posla")
    field_worker = models.BooleanField(verbose_name="Terenski radnik")
    office_worker = models.BooleanField(verbose_name="Kancelarijski radnik")
    assosiate = models.BooleanField(verbose_name="Saradnik")
    delivery_date = models.BooleanField(verbose_name="Datum izrade")
    cadastral_number = models.BooleanField(verbose_name="Broj predmeta u katastru")
    municipality = models.BooleanField(verbose_name="Opština")
    cadastral_price = models.BooleanField(verbose_name="Trošak katastra")
    subject_apply_date = models.BooleanField(verbose_name="Datum prijave predmeta")
    measuring_date = models.BooleanField(verbose_name="Datum merenja")
    field_lookup_date = models.BooleanField(verbose_name="Datum izlaska na teren")
    expected_finish_date = models.BooleanField(verbose_name="Završetak izrade predmeta")
    scanned_documents = models.BooleanField(verbose_name="Skenirani dokumenti")
    installation_length = models.BooleanField(verbose_name="Metara za instalaciju")
    elaborat = models.BooleanField(verbose_name="Elaborat")

    class Meta:
        verbose_name = 'Tip posla'
        verbose_name_plural = 'Tipovi poslova'

    def __str__(self):
        return self.name
    

class Katastar(models.Model):
    office = models.CharField(max_length=255, blank=True, null=True, verbose_name="Katastarska služba")
    municipality = models.CharField(max_length=255, blank=True, null=True, verbose_name="Opština")
    cadastral_municipality = models.CharField(max_length=255, blank=True, null=True, verbose_name="Katastarska opština")

    class Meta:
        verbose_name = 'Katastar'
        verbose_name_plural = 'Katastri'

    def __str__(self):
        return self.cadastral_municipality


class Subject(models.Model):
    service_type = models.ForeignKey(SubjectType, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Tip posla")
    cadastral_municipality = models.ForeignKey(Katastar, blank=True, null=True, on_delete=models.SET_NULL, related_name="katastarska_opstina", verbose_name="Katastarska opština")
    start_date = models.DateField(auto_now_add=True)
    field_worker = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, related_name="terenski", verbose_name="Terenski radnik")
    office_worker = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, related_name="kancelarijski", verbose_name="Kancelarijski radnik")
    responsible_worker = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, related_name="odgovorno", verbose_name="Odgovorno lice")
    assosiate = models.ForeignKey(Assosiate, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Saradnik")
    status = models.CharField(max_length=255, blank=True, null=True, verbose_name="Faza predmeta", default="POTREBNO PRIJAVITI RGZ-u")
    price = models.IntegerField(blank=True, null=True, verbose_name="Cena")
    cadastral_price = models.IntegerField(blank=True, null=True, verbose_name="Trošak katastra")
    payment_day = models.DateField(blank=True, null=True, verbose_name="Datum plaćanja")
    paid = models.BooleanField(verbose_name="Uplaćeno", default=False)
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Datum izrade")
    cadastral_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Broj predmeta u katastru")
    municipality = models.CharField(max_length=255, blank=True, null=True, verbose_name="Opština")
    subject_apply_date = models.DateField(blank=True, null=True, verbose_name="Datum prijave predmeta")
    data_returned = models.BooleanField(verbose_name="Podaci iz RGZ-a završeni", default=False)
    measuring_date = models.DateField(blank=True, null=True, verbose_name="Datum merenja")
    field_lookup_date = models.DateField(blank=True, null=True, verbose_name="Datum izlaska na teren")
    expected_finish_date = models.DateField(blank=True,null=True, verbose_name="Završetak izrade predmeta")
    scanned_documents = models.BooleanField(verbose_name="Skenirani dokumenti", default=False)
    installation_length = models.FloatField(blank=True, null=True, verbose_name="Metara za instalaciju")
    signed = models.BooleanField(verbose_name="Potpisan", default="False")
    canceled = models.BooleanField(verbose_name="Storniran", default="False")
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Kancelarija")
    opener = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, related_name="otvorio", verbose_name="Otvorio")
    users = models.ManyToManyField(CustomUser)
    clients = models.ManyToManyField(Client)

    class Meta:
        verbose_name = 'Predmet'
        verbose_name_plural = 'Predmeti'

    def __str__(self):
        return f'{self.id}'


class Comment(models.Model):
    author = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Korisnik")
    subject = models.ForeignKey(Subject, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Predmet")
    date = models.DateField(auto_now_add=True, verbose_name="Datum")
    text = models.TextField(verbose_name="Komentar")

    class Meta:
        verbose_name = 'Komentar'
        verbose_name_plural = 'Komentari'

    def __str__(self):
        return self.text
    

class Lot(models.Model):
    lot_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Broj parcele")
    subject = models.ForeignKey(Subject, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Predmet")

    class Meta:
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcele'

    def __str__(self):
        return self.lot_number
    

class LotObject(models.Model):
    lot = models.ForeignKey(Lot, blank=False, null=False, on_delete=models.CASCADE, verbose_name="Objekat")
    number = models.CharField(max_length=50, blank=False, null=False, verbose_name="Broj objekta")
    purpose = models.CharField(max_length=255, blank=False, null=False, verbose_name="Namena objekta")
    storey = models.CharField(max_length=255, blank=True, null=True, verbose_name="Spratnost")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Naziv objekta")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresa")
    owner = models.CharField(max_length=255, blank=True, null=True, verbose_name="Imalac prava")

    class Meta:
        verbose_name = 'Objekat'
        verbose_name_plural = 'Objekti'

    def __str__(self):
        return self.number
    

class GpsDevice(models.Model):
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kancelarija")
    manufacturer = models.CharField(max_length=255, blank=False, null=False, verbose_name="Proizvođač")
    model = models.CharField(max_length=255, blank=False, null=False, verbose_name="Model")
    serial_number = models.CharField(max_length=255, blank=False, null=False, verbose_name="Serijski broj")
    certificate = models.CharField(max_length=255, blank=False, null=False, verbose_name="Broj sertifikata")
    valid_until = models.DateField(blank=False, null=False, verbose_name="Važi do")
    type = models.CharField(max_length=255, blank=False, null=False, verbose_name="Tip aparata")

    class Meta:
        verbose_name = 'Instrument'
        verbose_name_plural = 'Instrumenti'

    def __str__(self):
        return f'{self.manufacturer} {self.model}'


class ElaboratDocument(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True, verbose_name="Naziv dokumenta")
    aws_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Naziv na AWS-u")
    template_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Broj obrasca")
    root = models.BooleanField(verbose_name="Root", default="False")
    grider = models.BooleanField(verbose_name="Grider", default="False")
    cad = models.BooleanField(verbose_name="CAD", default="False")
    content = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sadrzaj")
    subject = models.ForeignKey(Subject, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Predmet")

    class Meta:
        verbose_name = 'Elaborat dokument'
        verbose_name_plural = 'Elaborat dokumenti'

    def __str__(self):
        return self.name
    

class ElaboratType(models.Model):
    type = models.ForeignKey(SubjectType, blank=False, null=False, on_delete=models.CASCADE, verbose_name="Tip posla")
    document = models.ForeignKey(ElaboratDocument, blank=False, null=False, on_delete=models.CASCADE, verbose_name="Dokument")
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Tip elaborata'
        verbose_name_plural = 'Tipovi elaborata'

    def __str__(self):
        return self.type.name
    

class Elaborat(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, verbose_name="Ime elaborata")
    subject = models.ForeignKey(Subject, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Predmet")

    class Meta:
        verbose_name = 'Elaborat'
        verbose_name_plural = 'Elaborati'

    def __str__(self):
        return self.name        


class ElaboratSubjectDocument(models.Model):
    elaborat = models.ForeignKey(Elaborat, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Predmet")
    document = models.ForeignKey(ElaboratDocument, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Dokument")
    order = models.IntegerField(blank=True, null=True)
    uploaded = models.BooleanField(verbose_name="Uploaded", default=False)

    class Meta:
        verbose_name = 'Dokument predmeta'
        verbose_name_plural = 'Dokumenti predmeta'       