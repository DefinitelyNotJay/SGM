from django import forms
from store.models import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity_in_stock', 'categories']  # กำหนดฟิลด์ที่ต้องการในฟอร์ม

    # ถ้าต้องการกำหนดลักษณะเพิ่มเติมให้กับฟิลด์
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.all()  # กำหนด queryset สำหรับหมวดหมู่
