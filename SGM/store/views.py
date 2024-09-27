from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.views import View
from django.http import *
from store.models import *
from store.forms.authentication import *
from store.forms.customer import *
from store.forms.order import *
from store.forms.product import *
from django.forms.models import model_to_dict
from django.db.models import Sum, Count, F, Value
from datetime import datetime
from django.utils.timezone import *
import json
from store.forms.product import ProductForm
from django.utils import timezone
from django.db.models import *
from django.urls import reverse
from promptpay import qrcode
from io import BytesIO
# Create your views here.

class Inventory(View):
    def get(self, request):
        print(Customer.objects.all())
        return HttpResponse("123")
    
class ManageUserView(View):
    def get(self, request):
        
        return render(request, "employee/customer_form.html", {"form": CustomerCreateForm()})

class SignUp(View):
    def get(self, request):
        return render(request, "registration/sign_up.html", {"form": RegisterForm()})

class EmployeeHome(View):
    def get(self, request):
        return render(request, "employee/home.html")

class Stock(View):
    def get(self, request):
        categories = request.GET.getlist('category')  # รับ category จาก query parameters ที่อาจมีมากกว่า 1
        sort_filter = request.GET.get('sort_filter')  # รับตัวเลือกการกรองข้อมูล

        # กรณีไม่มีการเลือก category หรือ sort_filter ใด ๆ
        if not categories and not sort_filter:
            products = Product.objects.all().order_by('quantity_in_stock')
            categories = Category.objects.all()
            context = {'products': products, 'categories': categories}
            return render(request, "employee/stock.html", context)

        # หากมีการเลือก filter
        else:
            new_products = Product.objects.all()

            # มี sort_filter
            if sort_filter:
                if sort_filter == 'sales-asc':
                    new_products = Product.objects.annotate(total_sold=Sum('orderitem__amount')).order_by('total_sold')
                elif sort_filter == 'sales-desc':
                    new_products = Product.objects.annotate(total_sold=Sum('orderitem__amount')).order_by('-total_sold')
                elif sort_filter == 'quantity-asc':
                    new_products = Product.objects.order_by('quantity_in_stock')
                elif sort_filter == 'quantity-desc':
                    new_products = Product.objects.order_by('-quantity_in_stock')

            # มี categories
            if categories:
                new_products = new_products.filter(categories__name__in=categories).distinct()

            all_categories = Category.objects.all()
            context = {'products': new_products, 'categories': all_categories}
            return render(request, "employee/stock.html", context)
    def post(self, request):
        print(request.body)
        stock_amount = json.loads(request.body)
        for p in stock_amount:
            product = Product.objects.get(pk=p['id'])
            product.daily_restock_quantity = p['amount']
            product.save()
        return JsonResponse({'status': 'success'})

class Payment(View):
    def get(self, request, category=None):
        # มี query
        if category is None:
            products = Product.objects.all()
        else:
            # ทั้งหมด
            products = Product.objects.filter(categories__name=category)
        return render(request, "employee/payment.html", {"products": products})
    def post(self, request):
        post_data = request.POST.get('ordered_products')
        print(post_data)
        data = json.loads(post_data)
        if data:
            total = 0
            for product in data.get('storage_products'):
                product_time_amount = product['price'] * product['amount']
                product['price_amount'] = product_time_amount
                total += product_time_amount
            data['total'] = total
            return render(request, 'employee/payment_bill.html', data)
        return JsonResponse({"status": "error", "message": "ไม่มีสินค้าที่เลือก"})
class PaymentBill(View):
    def post(self, request):
        ordered_products = json.loads(request.body)
        products = ordered_products.get('storage_products')
        amount = int(ordered_products.get('storage_amount'))
        total = float(ordered_products.get('total'))
        customer_id = ordered_products.get('customer_id')
        payment_method = ordered_products.get('payment_method')
        
        try:
            customer = Customer.objects.filter(username=customer_id).first()
            order = Order.objects.create(customer=customer, total_price=total, quantity=amount, status='PAID', payment_method=payment_method)
            
            for product in products:
                OrderItem.objects.create(order=order, product=Product.objects.get(id=product['id']), amount=product['amount'])
                use_product = Product.objects.get(pk=product['id'])
                quantity = use_product.quantity_in_stock
                use_product.quantity_in_stock = quantity - product['amount']
                use_product.save()
                
            return JsonResponse({'status': 'complete'})
        except Exception as e:
            print(e)
            return HttpResponse(e)

class GenerateQRCode(View):
    def get(self, request):
        amount = request.GET.get('amount')
        customer_id = '0802695576'

        payload_with_amount = qrcode.generate_payload(customer_id, float(amount))

        img = qrcode.to_image(payload_with_amount)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type="image/png")

class ListCustomer(View):
    def get(self, request):
        customers = Customer.objects.all()
        return render(request, "employee/all_customer.html", {"customers": customers})

class ManageCustomer(View):
    def get(self, request, customer_id=None):
        if(customer_id):
            # edit customer info
            customer_instance = Customer.objects.get(pk=customer_id)
            edit_form = CustomerCreateForm(initial=model_to_dict(customer_instance), instance=customer_instance)
            context = {"form": edit_form, "customer": customer_instance}
            return render(request, "employee/customer_form.html", context)
        return render(request, "employee/customer_form.html", {"form": CustomerCreateForm(), "isCreate": True})

        # get all customers
    def post(self, request, customer_id=None):
        if customer_id:
            customer_instance = Customer.objects.get(pk=customer_id)
            form = CustomerCreateForm(request.POST, instance=customer_instance)
            if form.is_valid:
                try:
                    form.save()
                    return redirect("/customer")
                except:
                    return HttpResponseServerError()
        # create customer
        form = CustomerCreateForm(request.POST)
        if form.is_valid:
            try:
                form.save()
                return redirect("/customer")
            except:
                return redirect("/customer/new/")
        return redirect("/customer")

    def delete(self, request, customer_id):
        # delete customer
        try:
            Customer.objects.get(pk=customer_id).delete()
            return JsonResponse({"success": True})
        except:
            return HttpResponseBadRequest("ไม่มีผู้ใช้นี้ในระบบ")

class StatisticsView(View):
    MONTHS_EN_TO_TH = {
        "January": "มกราคม",
        "February": "กุมภาพันธ์",
        "March": "มีนาคม",
        "April": "เมษายน",
        "May": "พฤษภาคม",
        "June": "มิถุนายน",
        "July": "กรกฎาคม",
        "August": "สิงหาคม",
        "September": "กันยายน",
        "October": "ตุลาคม",
        "November": "พฤศจิกายน",
        "December": "ธันวาคม",
    }
    def get(self, request):
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        customers = Customer.objects.annotate(total_spent=Sum('order__total_price')).filter(
            order__date__month=current_month,
            order__date__year=current_year,
            total_spent__isnull=False)
       
        products = Product.objects.annotate(bestseller=Sum('orderitem__amount')).filter(
            orderitem__order__date__month=current_month,
            orderitem__order__date__year=current_year,
            bestseller__isnull=False).order_by('-bestseller')
    
        allcustomer = Customer.objects.all().count()

        current_date = now()
        current_month_name_en = current_date.strftime("%B")
        current_month_name_th = self.MONTHS_EN_TO_TH.get(current_month_name_en, current_month_name_en)


        return render(request, 'statistics.html', {'customers': customers , 'products':products, 'allcustomer':allcustomer, 'current_month_name_th': current_month_name_th})

class ViewStock(View):
    def get(self, request):
        products = Product.objects.all()  # ดึงสินค้าทั้งหมด
        return render(request, 'index.html', {'products': products})

class ManageInventory(View):
    def get(self, request, category_name=None):
        # ถ้ามีการระบุหมวดหมู่ใน URL ให้ทำการกรองสินค้าตามหมวดหมู่
        if category_name:
            category = get_object_or_404(Category, name=category_name)
            products = Product.objects.filter(categories=category)
            category_name = category
            
        else:
            products = Product.objects.all()
            category_name = "ทั้งหมด"

        return render(request, 'manageInventory.html', {
            'products': products,
            'category_name': category_name,
        })

    def post(self, request, category_name=None, *args, **kwargs):
        product_id = request.POST.get('product_id')  # รับ product_id จากฟอร์ม
        if product_id:
          # สร้าง URL สำหรับไปยัง view ที่ใช้แก้ไขผลิตภัณฑ์ โดยส่ง category_name ด้วย
            return redirect(reverse('editProduct', kwargs={'product_id': product_id}))
        else:
            # หากไม่มี product_id ให้ redirect กลับไปยังหน้าเดิม
            return redirect('manage_inventory', category_name=category_name)
        
class Editproduct(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(instance=product)  # สร้างฟอร์มจากอินสแตนซ์ของผลิตภัณฑ์
        return render(request, 'editProduct.html', {'form': form, 'product': product})

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST, instance=product)  # สร้างฟอร์มจากข้อมูลที่ส่งมา

        if form.is_valid():
            form.save()  # บันทึกข้อมูลที่แก้ไข
            return redirect('manageInventory')  # เปลี่ยนเส้นทางกลับไปที่หน้า Manage Inventory

        return render(request, 'editProduct.html', {'form': form, 'product': product})  # หากฟอร์มไม่ถูกต้อง ให้แสดงฟอร์มอีกครั้ง

class DeleteProduct(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()  # ลบสินค้า
        return redirect('manageInventory')  # กลับไปที่หน้า manageInventory


class AddProduct(View):
    def get(self, request):
        form = ProductForm()
        return render(request, 'addProduct.html', {'form': form})

    def post(self, request):
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()  # บันทึกสินค้าใหม่
            return redirect('manageInventory') 
        return render(request, 'addProduct.html', {'form': form})