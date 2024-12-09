from django import forms
from django_flatpickr.widgets import DatePickerInput
from .models import Comment, GpsDevice, Lot, LotObject, SubjectType, Subject, CustomUser, Assosiate, Katastar
from accounts.models import Client

class RegisterSubjectForm(forms.Form):
    
    tip_posla = forms.ModelChoiceField(queryset=SubjectType.objects.all())


class EditSubjectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        self.fields['field_worker'] = forms.ModelChoiceField(queryset=CustomUser.objects.filter(company=self.current_user.company), required=False)
        self.fields['office_worker'] = forms.ModelChoiceField(queryset=CustomUser.objects.filter(company=self.current_user.company), required=False)
        self.fields['responsible_worker'] = forms.ModelChoiceField(queryset=CustomUser.objects.exclude(licence_number__isnull=True).filter(company=self.current_user.company), required=False)
        self.fields['assosiate'] = forms.ModelChoiceField(queryset=Assosiate.objects.filter(company=self.current_user.company), required=False)
        self.fields['cadastral_municipality'] = forms.ModelChoiceField(queryset=Katastar.objects.all(), required=False)

    class Meta:
        model = Subject
        fields = ['cadastral_municipality',
                  'field_worker',
                  'office_worker',
                  'responsible_worker',
                  'assosiate',
                  'status',
                  'price',
                  'cadastral_price',
                  'payment_day',
                  'paid',
                  'delivery_date',
                  'cadastral_number',
                  'municipality',
                  'subject_apply_date',
                  'data_returned',
                  'measuring_date',
                  'field_lookup_date',
                  'expected_finish_date',
                  'scanned_documents',
                  'installation_length',
                  'signed',
                  'canceled'
                ]
        widgets = {
                'payment_day': DatePickerInput(),
                'delivery_date': DatePickerInput(),
                'subject_apply_date': DatePickerInput(),
                'measuring_date': DatePickerInput(),
                'field_lookup_date': DatePickerInput(),
                'expected_finish_date': DatePickerInput()
            }
        
        def clean(self):
            return self.cleaned_data
        

class AddLotForm(forms.ModelForm):

    class Meta:
        model = Lot
        fields = ['lot_number']


class AddLotObjectForm(forms.ModelForm):

    class Meta:
        model = LotObject
        fields = ['number', 'purpose', 'storey', 'name', 'address', 'owner']


class AddCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']


class EditGpsDeviceForm(forms.ModelForm):

    type = forms.ChoiceField(choices=[('total', 'Totalna stanica'), ('gps', 'Gps instrument')])

    class Meta:
        model = GpsDevice
        fields = '__all__'
        widgets = {
                'valid_until': DatePickerInput(),
            }