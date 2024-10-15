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

 
class EmployeeCreateForm(UserCreationForm):
    """
    ฟอร์มการสร้างพนักงาน
    """
    class Meta:
        model = User
        fields = ["username", "password1", "password2", "first_name", "last_name", "email"]

class UserUpdateForm(forms.ModelForm):
    """
    ฟอร์มการ update user
    """
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]




class CustomerUserForm(forms.Form):
    """
    เพื่อเลี่ยงการใส่รหัสตามที่ UserCreationForm ต้องการ ; ลูกค้าไม่ควรกรอกรหัสที่มีเงื่อนไขมากเกินไป
    """
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
    


class ChangePasswordForm(forms.Form):
    """
    ฟอร์มการเปลี่ยนรหัสผ่าน
    """
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        new_pass = cleaned_data.get('new_password')
        confirm_pass = cleaned_data.get('confirm_password')

        if new_pass != confirm_pass:
            message = 'รหัสผ่านทั้ง 2 ช่องต้องตรงกัน'
            self.add_error("password1", message)
            self.add_error("password2", message)
        return cleaned_data
        
        


class CustomerCreateForm(ModelForm):
    """
    ฟอร์มการสร้าง Cutomer
    """
    class Meta:
        model = Customer
        fields = ["nickname", "gender", "notes"]
