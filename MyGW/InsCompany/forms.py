import django.contrib.auth.models as authmodel
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import *
from .models import *


class Login(forms.Form):
    username = forms.CharField(min_length=4, widget=forms.TextInput(attrs={'placeholder': 'Введите логин'}), required=True)
    password = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'placeholder': 'Введите текущий пароль'}), required=True)
    new_password = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'placeholder': 'Введите новый пароль'}))
    new_password2 = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите пароль'}))


class ResetForm(forms.Form):
    username = forms.CharField(min_length=4, widget=forms.TextInput(attrs={'placeholder': 'Введите логин'}), required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Введите рабочую почту'}))


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['tpr_surname', 'tpr_forename', 'tpr_middle', 'tpr_born_date', 'tpr_main_doc', 'tpr_psycho', 'tpr_unprofit']
        widgets = {
            'tpr_surname': forms.TextInput(attrs={"size": 50}),
            'tpr_forename': forms.TextInput(attrs={"size": 50}),
            'tpr_middle': forms.TextInput(attrs={"size": 50}),
            'tpr_born_date': forms.TextInput(attrs={"size": 50}),
            'tpr_main_doc': forms.TextInput(attrs={"size": 50}),
            'tpr_psycho': forms.CheckboxInput(attrs={"size": 50}),
            'tpr_unprofit': forms.CheckboxInput(attrs={"size": 50})
        }


class ContractNewForm(forms.Form):
    surname = forms.CharField(max_length=80, widget=forms.TextInput(attrs={"size": 50}))
    forename = forms.CharField(max_length=80, widget=forms.TextInput(attrs={"size": 50}))
    middle = forms.CharField(max_length=80, widget=forms.TextInput(attrs={"size": 50}))
    born_date = forms.DateField(widget=forms.TextInput(attrs={"size": 50}))
    main_doc = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"size": 50}))
    tco_length = forms.IntegerField(max_value=50, widget=forms.TextInput(attrs={"size": 50}))
    addr = forms.CharField(widget=Textarea(attrs={"rows": 5, "cols": 52}), required=False)
    mail = forms.EmailField(required=False, widget=forms.TextInput(attrs={"size": 50}))
    contact = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={"size": 50}))


class DealerNewForm(forms.Form):
    surname = forms.CharField(max_length=80, widget=forms.TextInput(attrs={"size": 50}))
    forename = forms.CharField(max_length=80, widget=forms.TextInput(attrs={"size": 50}))
    middle = forms.CharField(max_length=80, widget=forms.TextInput(attrs={"size": 50}))
    born_date = forms.DateField(widget=forms.TextInput(attrs={"size": 50}))
    main_doc = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"size": 50}))
    tde_start = forms.DateField(widget=forms.TextInput(attrs={"size": 50}))
    user_login = forms.CharField(widget=forms.TextInput(attrs={"size": 50}))
    work_mail = forms.EmailField(widget=forms.TextInput(attrs={"size": 50}))
    photo = forms.ImageField()


class NewWorker(forms.Form):
    user_login = forms.CharField(widget=forms.TextInput(attrs={"size": 50}))
    work_mail = forms.EmailField(widget=forms.TextInput(attrs={"size": 50}))
    photo = forms.ImageField()


class NewInsEvent(forms.Form):
    tiv_date = forms.DateField(widget=forms.TextInput(attrs={"size": 50}))
    tiv_time = forms.TimeField(widget=forms.TextInput(attrs={"size": 50}))
    tiv_desc = forms.CharField(widget=Textarea(attrs={"rows": 10, "cols": 52}), required=False)


class ElemClaimForm(forms.ModelForm):
    class Meta:
        model = ElemClaim
        fields = ['tel_sum_fact']
        widgets = {
            'tel_sum_fact': forms.TextInput(attrs={"size": 50})
        }


class NewContact(forms.Form):
    contact = forms.CharField(required=True, widget=forms.TextInput(attrs={"size": 50}))


class NewDocument(forms.Form):
    series = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={"size": 50}))
    doc_num = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={"size": 50}))
    issue_date = forms.DateField(required=True, widget=forms.TextInput(attrs={"size": 50}))
    issue_org = forms.CharField(max_length=255, required=True, widget=Textarea(attrs={"rows": 10, "cols": 52}))


class NewAddress(forms.Form):
    address = forms.CharField(required=True, widget=Textarea(attrs={"rows": 10, "cols": 52}),)




