from django.http.request import HttpRequest as HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.views import View
from django.http import *
from store.models import *
from store.forms.authentication import *
from store.forms.order import *
from store.forms.product import *
from django.forms.models import model_to_dict
from django.db.models import Sum, Count, F, Value, Q
from datetime import datetime
from django.utils.timezone import *
import json
from store.forms.product import ProductForm
from django.db.models import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from promptpay import qrcode
from io import BytesIO
from django.contrib.auth.models import Group, User
from .s3 import upload_file, get_client
from store.utils.sort import sort_products
from store.forms.CategoryForm import *
from django.db.models.functions import Coalesce



# Create your views here.

class Stock(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.view_order', 'store.add_order', 'store.change_order', 'store.delete_order']
    login_url = '/login/'
    
    def get(self, request):
        categories = request.GET.getlist('category') # รับ category จาก query parameters ที่อาจมีมากกว่า 1
        sort_filter = request.GET.get('sort_filter')  # รับตัวเลือกการกรองข้อมูล
        context = sort_products(categories, sort_filter)
        return render(request, "manager/stock.html", context)

    def post(self, request):
        stock_amount = json.loads(request.body)
        # stock_amount = [{'id': 1, 'amount': 51}, {'id': 3, 'amount': 60}] 
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
        products = ordered_products.get('storage_products')
        amount = int(ordered_products.get('storage_amount'))
        total = float(ordered_products.get('total'))
        customer_id = ordered_products.get('customer_id')
        payment_method = ordered_products.get('payment_method')


        try:
            order = None
            if customer_id:
                customer = Customer.objects.filter(user__username=customer_id).first()
                
                if not customer:
                    return HttpResponseNotFound("ไม่มีบัญชีนี้ในระบบ")
        
                loyaltyPoint = LoyaltyPoints.objects.get_or_create(customer_id=customer.id)

                order = Order.objects.create(customer=customer, total_price=total, quantity=amount, status='PAID', payment_method=payment_method)
            else:
                order = Order.objects.create(customer=None, total_price=total, quantity=amount, status='PAID', payment_method=payment_method)
                
            total_cost = 0

            for product in products:
                
                OrderItem.objects.create(order=order, product=Product.objects.get(id=product['id']), amount=product['amount'])

                use_product = Product.objects.get(pk=product['id'])
                quantity = use_product.quantity_in_stock

                use_product.quantity_in_stock = quantity - product['amount']
                use_product.save()

                total_cost += use_product.price * product['amount']
            
            if customer_id:
                print(loyaltyPoint[0].points, total_cost, (total_cost // 50))
                loyaltyPoint[0].points = loyaltyPoint[0].points + (total_cost // 50)
                loyaltyPoint[0].save()

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
        
        print(current_month, current_year)

        # รับคะแนนสะสม
        customers = Customer.objects.annotate(
    total_spent=Sum('order__total_price', filter=Q(order__date__month=current_month, order__date__year=current_year))).filter(total_spent__isnull=False).annotate(
    loyalty_points=F('loyaltypoints__points')).order_by('-total_spent')

        products = Product.objects.annotate(
        total_sold=Sum('orderitem__amount', filter=Q(orderitem__order__date__month=current_month, orderitem__order__date__year=current_year))).filter(total_sold__gt=0).order_by('-total_sold')

        for product in products:
            print(f"Product: {product.name}, bestseller: {product.total_sold}")

        allcustomer = Customer.objects.all().count()

        current_date = now()
        current_month_name_en = current_date.strftime("%B")
        current_month_name_th = self.MONTHS_EN_TO_TH.get(current_month_name_en, current_month_name_en)

        return render(request, 'manager/statistics.html', {
            'customers': customers,
            'products': products,
            'allcustomer': allcustomer,
            'current_month_name_th': current_month_name_th,
        })
    
class ViewStock(View):
    def get(self, request):
        categories_obj = Category.objects.all().values("name")
        categories = [cate.get("name") for cate in categories_obj]
        category = request.GET.get("category")
        title = ''
        products_new = []
        if category is None:
            products = Product.objects.annotate(total_sale=Sum(F('orderitem__amount'))
                                                ).filter(total_sale__isnull=False).order_by('-total_sale')[:5]  # แสดงเฉพาะ 5 อันดับแรกของสินค้าที่ขายดีที่สุด
            for product in products:
                print(f"Product: {product.name}, Total Sale: {product.total_sale}")

            products_new = Product.objects.all().order_by('-add_date')[:5] # แสดงสินค้าใหม่ 5 อันดับ
            title='สินค้าขายดี'
            print(products)
        elif category=='all':
            products = Product.objects.all()
            title='ทั้งหมด'
        else:
            if category not in categories:
                return redirect('/')
        
            products = Product.objects.filter(categories__name=category)
            title = category
        return render(request, 'customer/index.html', {'products': products, "products_new": products_new, "title": title, "categories": categories_obj})

class ManageInventory(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.view_product', 'store.add_product', 'store.change_product', 'store.delete_product']
    login_url = '/login/'

    def get(self, request, category_name=None):
        categories = Category.objects.all()  # ดึงหมวดหมู่ทั้งหมดมา
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
            'categories': categories,
        })

    def post(self, request, category_name=None, *args, **kwargs):
        product_id = request.POST.get('product_id')  # รับ product_id จากฟอร์ม
        return redirect('editProduct', product_id=product_id)  # เปลี่ยนเส้นทางไปที่ view แก้ไขผลิตภัณฑ์

class Editproduct(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.change_product']
    login_url = '/login/'

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(instance=product)  # สร้างฟอร์มจากอินสแตนซ์ของผลิตภัณฑ์
        return render(request, 'manager/editProduct.html', {'form': form, 'product': product})

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        form = ProductForm(request.POST, instance=product)  # สร้างฟอร์มจากข้อมูลที่ส่งมา
        if form.is_valid():
            # เช็คก่อนว่า input image มารึป่าว
            if not request.FILES:
                form.save()
                return redirect('/manageInventory')
            product = form.save()  # บันทึกข้อมูลที่แก้ไข
            # delete old image
            if product.image_url:
                image_key = (product.image_url).split('/')[-1]
                client = get_client()
                client.delete_object(Bucket="serverside-sgm", Key=image_key)
            # put new image to bucket
            image_file = request.FILES.get('image')
            sucess = upload_file(image_file, 'serverside-sgm')
            if sucess:
                # save new image path to image_url field
                image_url = f'https://serverside-sgm.s3.amazonaws.com/{image_file.name}'
                product.image_url = image_url
                product.save()
            
            return redirect('manageInventory')  # เปลี่ยนเส้นทางกลับไปที่หน้า Manage Inventory

        return render(request, 'manager/editProduct.html', {'form': form, 'product': product})  # หากฟอร์มไม่ถูกต้อง ให้แสดงฟอร์มอีกครั้ง

class DeleteProduct(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.delete_product']
    login_url = '/login/'
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()  # ลบสินค้า
        # return redirect('manageInventory')  # กลับไปที่หน้า manageInventory
        return JsonResponse({"success": True})


class AddProduct(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.add_product']
    login_url = '/login/'

    def get(self, request):
        form = ProductForm()
        return render(request, 'manager/addProduct.html', {'form': form})

    def post(self, request):
        print('files :', request.FILES)
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
    
class ManageCategories(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.view_category']
    login_url = '/login/'

    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'manager/manageCategories.html', {'categories': categories})

class AddCategory(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.add_category']
    login_url = '/login/'

    def get(self, request):
        form = CategoryForm()
        return render(request, 'manager/addCategory.html', {'form': form})

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manageCategories')
        return render(request, 'manager/addCategory.html', {'form': form})

class EditCategory(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.change_category']
    login_url = '/login/'

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        form = CategoryForm(instance=category)
        return render(request, 'manager/addCategory.html', {'form': form, 'category': category})

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('manageCategories')
        return render(request, 'manager/addCategory.html', {'form': form, 'category': category})

class DeleteCategory(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['store.delete_category']
    login_url = '/login/'

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return redirect('manageCategories')
    
class CustomerList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url='/login/'
    permission_required = ['store.add_customer', 'store.view_customer', 'store.change_customer']

    def get(self, request):
        customers = Customer.objects.all()
        context = {'title': 'ลูกค้า', 'customers': customers}
        return render(request, 'manager/account.html', context)

class ManageCustomer(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, customer_id):
        """
         แสดงฟอร์มการแก้ไขข้อมูล Customer
        """

        if request.user.customer.id != customer_id:
            return redirect(f'/customer/{request.user.customer.id}')

        customer_instance = Customer.objects.get(pk=customer_id)
        user_instance = User.objects.get(customer__id=customer_id)

        password_form = ChangePasswordForm()

        edit_form = CustomerCreateForm(initial=model_to_dict(customer_instance), instance=customer_instance)
        auth_form = UserUpdateForm(initial=model_to_dict(user_instance))

        context = {"form": edit_form, "customer": customer_instance, "form_auth": auth_form, "isCreate": False, "password_form": password_form}
        return render(request, "employee/customer_form.html", context)
            

        # get all customers
    def post(self, request, customer_id):
        """
        บัยทึกฟอร์ม Customer
        """
        # edit customer
        customer_instance = Customer.objects.get(pk=customer_id)
        form = CustomerCreateForm(request.POST, instance=customer_instance)
        if form.is_valid():
            try:
                form.save()
                return redirect("/")
            except Exception as e:
                return HttpResponseServerError()
    
    def delete(self, request, customer_id):
        """
        ลบ Customer ออกจากระบบ
        """
        
        if not request.user.is_staff:
            return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบบัญชีผู้ใช้งาน")
        
        try:
            User.objects.get(customer__id=customer_id).delete()
            return JsonResponse({"success": True})
        except:
            return HttpResponseBadRequest("ไม่มีผู้ใช้นี้ในระบบ")

class CreateCustomer(View):
    """
        create customer; all role can access
    """
    def get(self, request):
        return render(request, "employee/customer_form.html", {"form": CustomerCreateForm(), "form_auth": CustomerUserForm(), "isCreate": True})
    def post(self, request):
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
                # เพิ่ม customer group ให้ ลูกค้า
                user_group = Group.objects.get(name='customer')
                user.groups.add(user_group)
                user.save()


                # บันทึกข้อมูล user_id ลงใน customer instance
                customer = form.save(commit=False)
                customer.user_id = user.id
                customer.save()

                return redirect("/")
            except Exception as e:
                return render(request, 'employee/customer_form.html', {"form": form, "form_auth": form_auth, "isCreate": True})
        else:
            # แสดงผล errors ของฟอร์มเมื่อ validation ไม่ผ่าน
            return render(request, 'employee/customer_form.html', {"form": form, "form_auth": form_auth, "isCreate": True})

class EmployeeList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required=['auth.view_user']
    def get(self, request):
        employees = User.objects.filter(Q(is_staff=False) and Q(customer=None))
        context = {'title': 'พนักงาน', 'employees': employees}
        return render(request, 'manager/account.html', context)
    

class CreateEmployee(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.add_user', 'auth.view_user']

    def get(self, request):
        """
        แสดงฟอร์มการสร้าง Customer
        """
         
        form = EmployeeCreateForm()
        context = {"form": form}
        return render(request, './registration/sign-up.html', context)

    def post(self, request):
        """
        ฟอร์มรองรับการสร้าง Customer
        """
         
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data.get("password1"))
            employee_group = Group.objects.get(name='employee')
            user.groups.add(employee_group)
            user.save()
            return redirect('/login/')
        return render(request, './registration/sign-up.html', {'form': form})

class ManageEmployee(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    def test_func(self):
        """

        """
        return not self.request.user.groups.filter(name='customer').exists()
        
    
    def get(self, request, emp_id=None):
        """"
        แสดง Form การแก้ไข Employee
        """
        if request.user.id != emp_id:
            # หาก employee พยายามแก้ url เพื่อไปแก้ข้อมูลคนอื่นจะถูกส่งกลับไปที่ id ตนเอง
            return redirect(f'/employee/{request.user.id}/')
            # แก้ไขบัญชีพนักงาน
        emp_ins = User.objects.get(pk=emp_id)
        edit_form = EmployeeCreateForm(initial=model_to_dict(emp_ins), instance=emp_ins)
        password_form = ChangePasswordForm()
        context = {"form": edit_form, "password_form": password_form, "customer": emp_ins}
        return render(request, "manager/employee_form.html", context)
        
    def post(self, request, emp_id):
        """
        บันทึก form จากการ post
        """
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
                return redirect("/")  # กลับไปที่หน้าแสดงรายการ employee
            except Exception as e:
                return HttpResponseServerError(f"Error saving form: {str(e)}")
        else:
            # กรณีฟอร์มไม่ valid ให้แสดงฟอร์มและ error message
            return render(request, 'manager/employee_form.html', {'form': form, 'errors': form.errors})

    def delete(self, request, emp_id):
        """
        
        """
        if not request.user.is_staff:
            return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบพนักงาน")
        try:
            User.objects.get(pk=emp_id).delete()
            return JsonResponse({"success": True})
        except:
            return HttpResponseBadRequest("ไม่มีผู้ใช้นี้ในระบบ")
        

class Viewpoint(View):
    def get(self, request):
        # ดึงข้อมูล Customer ที่เชื่อมโยงกับ user ปัจจุบัน
        customer = Customer.objects.get(user=request.user)
        
        # ยอดที่ใช้จ่ายของลูกค้าคนปัจจุบัน
        my_spent = Order.objects.filter(customer=customer, status='PAID').aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # คำนวณคะแนนของลูกค้าคนปัจจุบัน (1 point per 50 THB spent)
        mypoints = my_spent // 50  

        # ตรวจสอบให้มั่นใจว่า mypoints ไม่เป็น null และตั้งค่าเริ่มต้นเป็น 0 หากพบว่าเป็น null
        mypoints = mypoints if mypoints is not None else 0

        # บันทึกหรืออัปเดตคะแนนสะสมลงใน LoyaltyPoints
        loyalty_record, created = LoyaltyPoints.objects.get_or_create(customer=customer, defaults={'points': mypoints})

        if not created:  # ถ้าเรคคอร์ดมีอยู่แล้ว ให้อัปเดตคะแนนใหม่
            loyalty_record.points = mypoints
            loyalty_record.save()

        # ดึงข้อมูลลูกค้าที่มียอดใช้จ่ายมากที่สุด 5 คน พร้อมคะแนน
        top_customers_data = (
            Order.objects.filter(customer__isnull=False, status='PAID')
            .select_related('customer__user')  # ใช้ select_related() ก่อน
            .values('customer', 'customer__user__first_name', 'customer__user__last_name','customer__user__username')  # เพิ่มฟิลด์ที่ต้องการ
            .annotate(total_spent=Sum('total_price'))
            .order_by('-total_spent')[:5]
        )
        
        # คำนวณคะแนนสำหรับลูกค้าแต่ละคน
        for customer_data in top_customers_data:
            customer_data['total_point'] = customer_data['total_spent'] // 50  # คำนวณคะแนน

        return render(request, 'customer/viewpoint.html', {
            'my_spent': my_spent, 
            'mypoints': mypoints,
            'top_customers_data': top_customers_data,
        })