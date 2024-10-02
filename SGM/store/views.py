from django.http.request import HttpRequest as HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
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
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from promptpay import qrcode
from io import BytesIO
from django.contrib.auth.models import Permission
from .s3 import upload_file, get_client
from store.utils.sort import sort_products


# Create your views here.
class EmployeeHome(LoginRequiredMixin, View):
    login_url = '/login/'
    # permission_required = ['store.create_order', 'store.add_order', 'store.change_order', 'store.view_order']
    def get(self, request):
        return redirect('/payment')

# Create your views here.

class Inventory(View):
    def get(self, request):
        print(Customer.objects.all())
        return HttpResponse("123")

class Stock(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.view_order', 'store.add_order', 'store.change_order', 'store.delete_order']
    login_url = '/login/'
    
    def get(self, request):
        categories = request.GET.getlist('category')  # รับ category จาก query parameters ที่อาจมีมากกว่า 1
        sort_filter = request.GET.get('sort_filter')  # รับตัวเลือกการกรองข้อมูล
        context = sort_products(categories, sort_filter)
        return render(request, "manager/stock.html", context)

    def post(self, request):
        stock_amount = json.loads(request.body)
        for p in stock_amount:
            product = Product.objects.get(pk=p['id'])
            product.daily_restock_quantity = p['amount']
            product.save()
        return JsonResponse({'status': 'success'})

class Payment(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.view_order', 'store.add_order', 'store.change_order']
    login_url = '/login/'
    def get(self, request):
        # มี query
        categories = request.GET.getlist('category') if 'category' in request.GET else None  # รับ category จาก query parameters ที่อาจมีมากกว่า 1
        sort_filter = request.GET['sort_filter'] if 'sort_filter' in request.GET else None  # รับตัวเลือกการกรองข้อมูล
        context = sort_products(categories, sort_filter)
        return render(request, 'employee/payment.html', context)
    def post(self, request):
        post_data = request.POST.get('ordered_products')
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



class PaymentBill(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.view_order', 'store.add_order', 'store.change_order']
    login_url = '/login/'
    def post(self, request):
        ordered_products = json.loads(request.body)
        print(ordered_products)
        products = ordered_products.get('storage_products')
        amount = int(ordered_products.get('storage_amount'))
        total = float(ordered_products.get('total'))
        customer_id = ordered_products.get('customer_id')
        payment_method = ordered_products.get('payment_method')
        
        try:
            customer = Customer.objects.filter(user__username=customer_id).first()
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

class ListCustomer(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.view_customer']
    login_url = '/login/'
    def get(self, request):
        customers = Customer.objects.all()
        return render(request, "employee/all_customer.html", {"customers": customers})


class StatisticsView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    def test_func(self):
        print(self.request.user.groups.all())
        return self.request.user.groups.filter(name='manager').exists()

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


        return render(request, 'manager/statistics.html', {'customers': customers , 'products':products, 'allcustomer':allcustomer, 'current_month_name_th': current_month_name_th})

class ViewStock(View):
    def get(self, request):
        # s3 = boto3.resource(
        # 's3',
        # aws_access_key_id= os.getenv('aws_access_key_id'),
        # aws_secret_access_key=os.getenv('aws_secret_access_key'),
        # aws_session_token= os.getenv('aws_session_token'),
        #     )

        # bucket = s3.Bucket('serversidesgm')
        # for obj in bucket.objects.all():
        #     print(obj.key)

        # for bucket in s3.buckets.all():
        #     print(bucket.name)
        
        # data=
        
        products = Product.objects.all()  # ดึงสินค้าทั้งหมด
        return render(request, 'customer/index.html', {'products': products})

class ManageInventory(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.view_product', 'store.add_product', 'store.change_product', 'store.delete_product']
    login_url = '/login/'
    CATEGORY_EN_TO_TH = {
        "Beverages": "เครื่องดื่ม",
        "Snacks": "ขนม",
        "Ice-cream": "ไอศกรีม",
        "Household-item": "ของใช้ครัวเรือน",
    }
    def get(self, request, category_name=None):
        # ถ้ามีการระบุหมวดหมู่ใน URL ให้ทำการกรองสินค้าตามหมวดหมู่
        if category_name:
            category = get_object_or_404(Category, name=category_name)
            products = Product.objects.filter(categories=category)
            category_name = category
            
        else:
            products = Product.objects.all()
            category_name = "ทั้งหมด"

        return render(request, 'manager/manageInventory.html', {
            'products': products,
            'category_name': category_name,
        })

    def post(self, request, category_name=None, *args, **kwargs):
        product_id = request.POST.get('product_id')  # รับ product_id จากฟอร์ม
        return redirect('editProduct', product_id=product_id)  # เปลี่ยนเส้นทางไปที่ view แก้ไขผลิตภัณฑ์

class Editproduct(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.change_product']
    login_url = '/login/'
        # if product_id:
        #   # สร้าง URL สำหรับไปยัง view ที่ใช้แก้ไขผลิตภัณฑ์ โดยส่ง category_name ด้วย
        #     return redirect(reverse('editProduct', kwargs={'product_id': product_id}))
        # else:
        #     # หากไม่มี product_id ให้ redirect กลับไปยังหน้าเดิม
        #     return redirect('manage_inventory', category_name=category_name)

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(instance=product)  # สร้างฟอร์มจากอินสแตนซ์ของผลิตภัณฑ์
        return render(request, 'manager/editProduct.html', {'form': form, 'product': product})

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST, instance=product)  # สร้างฟอร์มจากข้อมูลที่ส่งมา

        if form.is_valid():
            form.save()  # บันทึกข้อมูลที่แก้ไข
            return redirect('manageInventory')  # เปลี่ยนเส้นทางกลับไปที่หน้า Manage Inventory

        return render(request, 'manager/editProduct.html', {'form': form, 'product': product})  # หากฟอร์มไม่ถูกต้อง ให้แสดงฟอร์มอีกครั้ง

class DeleteProduct(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.delete_product']
    login_url = '/login/'
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()  # ลบสินค้า
        return redirect('manageInventory')  # กลับไปที่หน้า manageInventory


class AddProduct(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.add_product']
    login_url = '/login/'
    def get(self, request):
        form = ProductForm()
        return render(request, 'manager/addProduct.html', {'form': form})

    def post(self, request):
        print(request.POST)
        print(request.FILES)
        form = ProductForm(request.POST)
        if(not request.FILES):
            form.add_error("image", "โปรดใส่ภาพสินค้า")
            return render(request, 'manager/addProduct.html', {'form': form})
        
        if form.is_valid():
            product = form.save()  # บันทึกสินค้าใหม่
            image_file = request.FILES['image']
            sucess = upload_file(image_file, 'serverside-sgm')
            if sucess:
                image_url = f'https://serverside-sgm.s3.amazonaws.com/{image_file.name}'
                product.image_url = image_url
                product.save()
                return redirect('manageInventory')
        # มีรูป, form ไม่ valid
        return render(request, 'manager/addProduct.html', {'form': form})
        

class EmployeeManagement(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required=['auth.add_user', 'auth.view_user', 'auth.change_user', 'auth.delete_user']
    def get(self, request):
        employees = User.objects.filter(is_staff=False)
        context = {'title': 'พนักงาน', 'employees': employees}
        return render(request, 'manager/account.html', context)

class CustomerManagement(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url='/login/'
    permission_required = ['store.add_customer', 'store.view_customer', 'store.change_customer']
    def get(self, request):
        customers = Customer.objects.all()
        context = {'title': 'ลูกค้า', 'customers': customers}
        return render(request, 'manager/account.html', context)

class ManageCustomer(View):
    # permission_required = ['store.view_customer', 'store.add_customer', 'store.change_customer', 'store.delete_customer']
    # login_url = '/login/'

    def get(self, request, customer_id=None):
        # สร้าง customer, user
        if(customer_id):
            # edit customer info
            customer_instance = Customer.objects.get(pk=customer_id)
            edit_form = CustomerCreateForm(initial=model_to_dict(customer_instance), instance=customer_instance)
            context = {"form": edit_form, "customer": customer_instance}
            return render(request, "employee/customer_form.html", context)
        return render(request, "employee/customer_form.html", {"form": CustomerCreateForm(), "form_auth": CustomerUserForm(), "isCreate": True})

        # get all customers
    def post(self, request, customer_id=None):
        if customer_id:
            customer_instance = Customer.objects.get(pk=customer_id)
            form = CustomerCreateForm(request.POST, instance=customer_instance)
            if form.is_valid():
                try:
                    form.save()
                    return redirect("/customer")
                except Exception as e:
                    print(e)
                    return HttpResponseServerError()
        
        # create customer
        form = CustomerCreateForm(request.POST)
        form_auth = CustomerUserForm(request.POST)
        if form.is_valid() and form_auth.is_valid():
            try:
                username = form_auth.cleaned_data.get('username')
                first_name = form_auth.cleaned_data.get('first_name')
                last_name = form_auth.cleaned_data.get('last_name')
                password = form_auth.cleaned_data.get('password1')

                # สร้าง User
                user = User.objects.create(
                    username=username, 
                    first_name=first_name, 
                    last_name=last_name
                )
                user.set_password(password)
                print("password", user.password)
                user.save()

                # บันทึกข้อมูล user_id ลงใน customer instance
                customer = form.save(commit=False)
                customer.user_id = user.id
                customer.save()

                return redirect("/customer")
            except Exception as e:
                return render(request, 'employee/customer_form.html', {"form": form, "form_auth": form_auth, "isCreate": True})
        else:
            # แสดงผล errors ของฟอร์มเมื่อ validation ไม่ผ่าน
            print(form.errors)
            print(form_auth.errors)
            return render(request, 'employee/customer_form.html', {"form": form, "form_auth": form_auth, "isCreate": True})


    def delete(self, request, customer_id):
        # delete customer
        print("delete_cus")
        try:
            Customer.objects.get(pk=customer_id).delete()
            return JsonResponse({"success": True})
        except:
            return HttpResponseBadRequest("ไม่มีผู้ใช้นี้ในระบบ")

class ManageUserView(View):
    # ไม่ใช่อันสร้างหลัก
    def get(self, request):
        form = CustomerCreateForm()
        return render(request, "employee/customer_form.html", {"form": form})

    def get(self, request):
        # print(request.user.has_perm('store.create_order'))
        return redirect('/payment')


class ManageEmployee(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required=['auth.add_user', 'auth.view_user', 'auth.change_user', 'auth.delete_user']
    login_url = '/login/'

    def get(self, request, emp_id):
        if(emp_id):
            # edit customer info
            emp_ins = User.objects.get(pk=emp_id)
            edit_form = RegisterForm(initial=model_to_dict(emp_ins), instance=emp_ins)
            context = {"form": edit_form, "customer": emp_ins}
            return render(request, "manager/employee_form.html", context)
        return render(request, "manager/employee_form.html", {"form": CustomerCreateForm(), "isCreate": True})

        # get all customers
    def post(self, request, emp_id=None):
        if emp_id:
            print(request.POST)
            try:
                # ดึง instance ของ User ที่ต้องการแก้ไข
                employee_instance = User.objects.get(pk=emp_id)
            except User.DoesNotExist:
                return HttpResponseServerError("User not found.")
            
            # สร้างฟอร์มโดยใช้ instance ที่ต้องการแก้ไข และข้อมูลที่ส่งมาใน request.POST
            form = UserUpdateForm(request.POST, instance=employee_instance)
            
            # ตรวจสอบความถูกต้องของฟอร์ม
            if form.is_valid():
                try:
                    form.save()  # บันทึกการแก้ไขลงใน database
                    return redirect("/employee")  # กลับไปที่หน้าแสดงรายการ employee
                except Exception as e:
                    return HttpResponseServerError(f"Error saving form: {str(e)}")
            else:
                # กรณีฟอร์มไม่ valid ให้แสดงฟอร์มและ error message
                return render(request, 'manager/employee_form.html', {'form': form, 'errors': form.errors})
        else:
            return HttpResponseServerError("Employee ID not provided.")
        # create customer
        # เดี๋ยวืทำ
        # form = CustomerCreateForm(request.POST)
        # if form.is_valid:
        #     try:
        #         form.save()
        #         return redirect("/customer")
        #     except:
        #         return redirect("/customer/new/")
        # return redirect("/customer")

    def delete(self, request, emp_id):
        # delete emp
        print("delete_emp")
        try:
            User.objects.get(pk=emp_id).delete()
            return JsonResponse({"success": True})
        except:
            return HttpResponseBadRequest("ไม่มีผู้ใช้นี้ในระบบ")
        
class Viewcustomer(View):
    def get(self, request):
        
        return render(request, 'customer/viewpoin.html',{})
