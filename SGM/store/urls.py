from django.contrib import admin
from django.urls import path, include
from django.http import *
from .views import *

def role_based_urlpatterns(request):
    return HttpResponse("Hey")

urlpatterns = [
    path('', Inventory.as_view(), name="inventory"),
    path('emp-home', EmployeeHome.as_view()),
    path('stock', Stock.as_view()),
    path('stock/', StockManagement.as_view()),
    path('payment', Payment.as_view()),
    path('payment/bill', PaymentBill.as_view()),
    path('payment/<str:category>', Payment.as_view()),
    path('customer/new/', ManageCustomer.as_view()),
    path('customer/', ListCustomer.as_view(), name="customer"),
    path('customer/<int:customer_id>/', ManageCustomer.as_view(), name="new-customer"),
    path('sign-up', SignUp.as_view(), name="sign-up"),
    path('statistics', StatisticsView.as_view(), name="statistics"),
    path('Viewproduct', ViewStock.as_view(), name="Viewproduct"),
    path('manageInventory', ManageInventory.as_view(), name="manageInventory"),
    path('manageInventory/<str:category_name>/', ManageInventory.as_view(), name='manageInvenCat'),
    path('editProduct/<int:product_id>/', Editproduct.as_view(), name="editProduct"),
    path('deleteProduct/<int:product_id>/', DeleteProduct.as_view(), name='delete_product'),
    path('addProduct/', AddProduct.as_view(), name='addProduct'),
]

