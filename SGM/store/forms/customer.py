from django.forms import CharField
from django.forms.models import ModelForm
from store.models import Customer

class CustomerCreateForm(ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"