from django import forms
from django.core.exceptions import ValidationError
from store.models import Category

class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        label='ชื่อ',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'กรุณากรอกชื่อหมวดหมู่'
        })
    )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        
        # ตรวจสอบว่าชื่อหมวดหมู่มีอยู่ในฐานข้อมูลหรือไม่
        if Category.objects.filter(name=name).exists():
            self.add_error("name", 'ชื่อหมวดหมู่นี้มีอยู่แล้ว กรุณากรอกชื่อใหม่')
        
        return name  # ส่งค่าที่ผ่านการตรวจสอบแล้วกลับไป
    
    class Meta:
        model = Category
        fields = ['name']  # ชื่อหมวดหมู่ที่คุณต้องการเพิ่ม
