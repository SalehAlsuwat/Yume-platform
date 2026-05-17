from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import CustomerProfile, OwnerProfile




phone_validator = RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')

User = get_user_model()


class CustomerSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name  = forms.CharField(max_length=150, required=True)
    email      = forms.EmailField(required=True)
    avatar     = forms.ImageField(required=False)
    phone_number      = forms.CharField(required=True,validators=[phone_validator])
   

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']


class OwnerSignUpForm(UserCreationForm):
    first_name   = forms.CharField(max_length=150, required=True)
    last_name    = forms.CharField(max_length=150, required=True)
    email        = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=200)
    commercial_reg = forms.CharField(max_length=100)
    avatar       = forms.ImageField(required=False)
    phone_number = forms.CharField(required=True,validators=[phone_validator])

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']


class SignInForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

# ========
# Form for the User model fields (shared by both roles)
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

# Customer profile fields
class CustomerProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['avatar', 'phone_number']

# Owner profile fields (includes company info)
class OwnerProfileEditForm(forms.ModelForm):
    class Meta:
        model = OwnerProfile
        fields = ['avatar', 'phone_number', 'company_name', 'commercial_reg']
