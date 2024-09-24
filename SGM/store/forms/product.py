from django import forms
from store.models import Category, Product

class ProductForm(forms.ModelForm):
    CATEGORY_EN_TO_TH = {
        "Beverages": "เครื่องดื่ม",
        "Snacks": "ขนม",
        "Ice-cream": "ไอศกรีม",
        "Household-item": "ของใช้ครัวเรือน",
    }

    quantity_in_stock = forms.IntegerField(
        label='จำนวนในสต็อก',  # เปลี่ยนชื่อ label
        widget=forms.NumberInput(attrs={
            'class': 'shadow appearance-none border rounded w-full mb-4 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
        }),
        min_value=0,  # กำหนดค่าต่ำสุดถ้าต้องการ
        initial=0     # กำหนดค่าเริ่มต้นถ้าต้องการ
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
        initial=0     # กำหนดค่าเริ่มต้นถ้าต้องการ
    )

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        label='หมวดหมู่สินค้า',  # เปลี่ยนชื่อ label
        widget=forms.SelectMultiple(attrs={
            'class': 'shadow border rounded w-full mb-4 py-2 px-3 text-gray-700 leading-tight focus:shadow-outline'
        })
    )

    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity_in_stock', 'categories']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # แปลชื่อหมวดหมู่
        self.fields['categories'].choices = self.get_translated_categories()

    def get_translated_categories(self):
        # ดึงหมวดหมู่ทั้งหมดจากฐานข้อมูล
        categories = Category.objects.all()
        # สร้างรายการตัวเลือกที่แปลเป็นภาษาไทย
        translated_choices = [
            (cat.id, self.CATEGORY_EN_TO_TH.get(cat.name, cat.name)) for cat in categories
        ]
        return translated_choices
