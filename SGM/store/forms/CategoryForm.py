# forms.py
from django import forms
from store.models import Category

class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        label='ชื่อ',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'กรุณากรอกชื่อหมวดหมู่'
        })
    )
    class Meta:
        model = Category
        fields = ['name']  # ชื่อหมวดหมู่ที่คุณต้องการเพิ่ม
