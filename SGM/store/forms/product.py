from django import forms
from store.models import Category, Product

class ProductForm(forms.ModelForm):
    quantity_in_stock = forms.IntegerField(
        label='จำนวนในสต็อก',  # เปลี่ยนชื่อ label
        widget=forms.NumberInput(attrs={
            'class': 'shadow appearance-none border rounded w-full mb-4 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
        }),
        min_value=0,  # กำหนดค่าต่ำสุดถ้าต้องการ
    )

    name = forms.CharField(
        label='ชื่อสินค้า',  # เปลี่ยนชื่อ label
        widget=forms.TextInput(attrs={
            'class': 'shadow border rounded w-full mb-4 py-2 px-3 text-gray-700 leading-tight focus:shadow-outline'
        })
    )

    price = forms.DecimalField(
        label='ราคา',  # เปลี่ยนชื่อ label
        widget=forms.NumberInput(attrs={
            'class': 'shadow border rounded w-full mb-4 py-2 px-3 text-gray-700 leading-tight focus:shadow-outline'
        }),
        min_value=0,  # กำหนดค่าต่ำสุดถ้าต้องการ
    )

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        label='หมวดหมู่สินค้า',  # เปลี่ยนชื่อ label
        widget=forms.SelectMultiple(attrs={
            'class': 'shadow border rounded w-full mb-4 py-2 px-3 text-gray-700 leading-tight focus:shadow-outline'
        })
    )
    
    image = forms.ImageField(
        label='อัปโหลดภาพสินค้า',  # เปลี่ยนชื่อ label
        required=False
    )

    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity_in_stock', 'categories', 'image']
    
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if Product.objects.filter(name=name).exists():
            self.add_error("name", "มีสินค้านี้อยู่แล้วในระบบ")
        return name
        
