from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from store.models import User, Customer
from django.forms.models import ModelForm
from django.contrib.auth.forms import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
 
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2", "first_name", "last_name", "email", "is_staff"]

class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput, 
        required=False
    )
    password2 = forms.CharField(
        label="Password confirmation", 
        widget=forms.PasswordInput, 
        required=False
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_staff"]

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords don't match.")
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # ตรวจสอบว่ามีการอัปเดต password หรือไม่
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        return user
