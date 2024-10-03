from typing import Any
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from store.models import User, Customer
from django.forms.models import ModelForm
from django.contrib.auth.forms import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form
from django import forms

 
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2", "first_name", "last_name", "email"]
    



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
        
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        return user

class CustomerUserForm(forms.Form):
    
    username = forms.CharField(max_length=10)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get('password1')
        pass2 = cleaned_data.get('password2')
        
        user = User.objects.filter(username=cleaned_data.get('username'))
        if(user.exists()):
            message = 'มีเบอร์โทรนี้อยู่ในระบบแล้ว'
            self.add_error("username", message)
      

        if pass1 != pass2:
            message = 'รหัสผ่านทั้ง 2 ช่องต้องตรงกัน'
            self.add_error("password1", message)
            self.add_error("password2", message)
        return cleaned_data