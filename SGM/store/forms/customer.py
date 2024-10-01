from django.forms import CharField, Form
from django.forms.models import ModelForm
from store.models import Customer

class CustomerCreateForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["nickname", "gender", "notes"]