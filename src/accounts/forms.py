from django import forms
from django_flatpickr.widgets import DatePickerInput
from django.contrib.auth.forms import AuthenticationForm
from .models import RegisterReq, CustomUser, Company, Assosiate, Client
from main.models import Subject


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = forms.EmailField()


class RegisterForm(forms.ModelForm):
    class Meta:
        model = RegisterReq
        fields = ['company_name', 'email']
    def clean(self):
        if RegisterReq.objects.filter(email=self.cleaned_data.get('email')):
            raise forms.ValidationError('Email vec postoji u zahtevima!')
        if CustomUser.objects.filter(email=self.cleaned_data.get('email')):
            raise forms.ValidationError('Email vec registrovan!')
        return self.cleaned_data
    

class RegisterUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'licence_number', 'can_open_subject', 'can_add_user', 'can_add_assosiate', 'can_add_client']

    def clean(self):
        if CustomUser.objects.filter(email=self.cleaned_data.get('email')):
            raise forms.ValidationError('Email vec registrovan!')
        if self.cleaned_data.get('first_name') == '':
            raise forms.ValidationError('Ime je obavezno!')
        if self.cleaned_data.get('last_name') == '':
            raise forms.ValidationError('Prezime je obavezno!')
        return self.cleaned_data
    

class RegisterClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'city', 'address', 'contact', 'email']

    def clean(self):
        if self.cleaned_data.get('name') == '':
            raise forms.ValidationError('Ime je obavezno!')
        if self.cleaned_data.get('contact') == '':
            raise forms.ValidationError('Kontakt je obavezan!')
        return self.cleaned_data
    

class EditClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'city', 'address', 'contact', 'email']

    def clean(self):
        if self.cleaned_data.get('first_name') == None:
            raise forms.ValidationError('Ime je obavezno!')
        if self.cleaned_data.get('last_name') == None:
            raise forms.ValidationError('Prezime je obavezno!')
        if self.cleaned_data.get('city') == None:
            raise forms.ValidationError('Mesto je obavezno!')
        if self.cleaned_data.get('address') == None:
            raise forms.ValidationError('Adresa je obavezna!')
        if self.cleaned_data.get('contact') == None:
            raise forms.ValidationError('Kontakt je obavezan!')
        return self.cleaned_data
    

class SelfEditClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'city', 'address', 'contact', 'email']
    
    def clean(self):
        if self.cleaned_data.get('email') == None:
            raise forms.ValidationError('Email je obavezan!')
        if self.cleaned_data.get('first_name') == None:
            raise forms.ValidationError('Ime je obavezno!')
        if self.cleaned_data.get('last_name') == None:
            raise forms.ValidationError('Prezime je obavezno!')
        if self.cleaned_data.get('city') == None:
            raise forms.ValidationError('Mesto je obavezno!')
        if self.cleaned_data.get('address') == None:
            raise forms.ValidationError('Adresa je obavezna!')
        if self.cleaned_data.get('contact') == None:
            raise forms.ValidationError('Kontakt je obavezan!')
        return self.cleaned_data

class ChooseClientForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        self.fields['clients'] = forms.ModelMultipleChoiceField(queryset=Client.objects.filter(company=self.current_user.company),
                                                                widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Subject
        fields = ['clients']
    

class RegisterAssosiateForm(forms.ModelForm):
    class Meta:
        model = Assosiate
        fields = ['first_name', 'last_name', 'email', 'profession']
    def clean(self):
        if Assosiate.objects.filter(email=self.cleaned_data.get('email')):
            raise forms.ValidationError('Email vec registrovan!')
        if self.cleaned_data.get('first_name') == '':
            raise forms.ValidationError('Ime je obavezno!')
        if self.cleaned_data.get('last_name') == '':
            raise forms.ValidationError('Prezime je obavezno!')
        return self.cleaned_data
    

class EditAssosiateForm(forms.ModelForm):
    class Meta:
        model = Assosiate
        fields = ['first_name', 'last_name', 'email', 'profession']
    def clean(self):
        if self.cleaned_data.get('email') == None:
            raise forms.ValidationError('Email je obavezan!')
        if self.cleaned_data.get('first_name') == None:
            raise forms.ValidationError('Ime je obavezno!')
        if self.cleaned_data.get('last_name') == None:
            raise forms.ValidationError('Prezime je obavezno!')
        return self.cleaned_data
    

class EditCompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = '__all__'
        widgets = {
                'foundation_date': DatePickerInput()
            }

    def clean(self):
        if self.cleaned_data.get('full_name') == None:
            raise forms.ValidationError('Puno ime je obavezno!')
        return self.cleaned_data
    

class EditUserForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'licence_number', 'telefon_number', 'education', 'can_open_subject', 'can_add_user', 'can_add_assosiate', 'can_add_client']

    def clean(self):
        if self.cleaned_data.get('email') == '':
            raise forms.ValidationError('Email je obavezan!')
        return self.cleaned_data
    

class SelfEditUserForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'licence_number', 'education', 'telefon_number']

    def clean(self):
        if self.cleaned_data.get('email') == '':
            raise forms.ValidationError('Email je obavezan!')
        return self.cleaned_data
