from django.shortcuts import render, redirect
from django.views import View
from django.http import *
from store.models import *
from .forms.authentication import *
from .forms.customer import *
from .forms.order import *
from django.forms.models import model_to_dict
from django.db.models import Sum, Count, F, Value
from datetime import datetime
from django.utils.timezone import *
import json

# Create your views here.

class Inventory(View):
    def get(self, request):
        return render(request, "employee/customer_form.html", {"form": CustomerCreateForm()})

class SignUp(View):
    def get(self, request):
        return render(request, "registration/sign_up.html", {"form": RegisterForm()})

class EmployeeHome(View):
    def get(self, request):
        return render(request, "employee/home.html")

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
        order_data = json.loads(request.body)
        print(order_data)
        if order_data:
            total_price = 0
            new_order = Order.objects.create(quantity=order_data.get("storage_amount"))
            for order in order_data.get("storage_products"):
                product_id = order.get("id")
                amount = order.get("amount")
                product = Product.objects.get(pk=product_id)
                # add cost to total_price
                total_price += product.price * amount
                # create orderItem
                new_orderItem = OrderItem.objects.create(order=new_order, product=product, amount=amount)
            new_order.total_price = total_price
            new_order.save()
            return JsonResponse({"status": "success", "order_id": new_order.id})
        return JsonResponse({"status": "error", "message": "ไม่มีสินค้าที่เลือก"})

class PaymentBill(View):
    def get(self, request):
        order = Order.objects.order_by("-id").first()
        print(order)
        orderItems = OrderItem.objects.filter(order=order).annotate(price=(F("amount") * F("product__price")))
        return render(request, "employee/payment_bill.html", {"form": OrderForm(), "order": order, "orderItems": orderItems})
    def post(self, request):
        order_data = json.loads(request.body)
        order_id = order_data.get("order_id")
        # ทำให้จำนวน product แต่ละตัวลด
        products_in_cart = order_data.get("storage_products")
        try:
            for data in products_in_cart:
                product = Product.objects.get(pk=data.get('id'))
                amount_in_stock = product.quantity_in_stock
                product.quantity_in_stock = amount_in_stock - data.get("amount")
                product.save()
        except Exception:
            return HttpResponseServerError("Products in cart went wrong !", Exception)
            
        # อัพเดท order นั้นให้มีสถานะเป็น 'PAID'
        try:
            order = Order.objects.get(pk=order_id)
            order.status = 'PAID'
            order.save()
        except Exception:
            return HttpResponseServerError("Order object error!", Exception)
        return JsonResponse({"success": True})

        

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
                customer = form.save()
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
