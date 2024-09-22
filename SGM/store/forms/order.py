from django.forms import ModelForm
from store.models import Order

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ["customer"]