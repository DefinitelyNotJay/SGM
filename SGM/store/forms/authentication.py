from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from store.models import User, Customer
from django.forms.models import ModelForm

class RegisterForm(ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"