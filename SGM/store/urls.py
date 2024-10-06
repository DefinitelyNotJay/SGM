from django.contrib import admin
from django.urls import path, include
from django.http import *
from .views import *
from . import views


urlpatterns = [
    # all
    path("", include('authen.urls')),
    
    # customer
    path('', ViewStock.as_view(), name="view-product"),
    # employee
    path('stock/', Stock.as_view()),
    path('payment/', Payment.as_view()),
    path('payment/bill', PaymentBill.as_view()),
    path('payment/generate-qrcode', GenerateQRCode.as_view(), name='generate_qrcode'),
    path('customer/', CustomerList.as_view(), name="customer-list"),
    path('customer/new/', CreateCustomer.as_view(), name="new-customer"),
    path('customer/<int:customer_id>/', ManageCustomer.as_view(), name="edit-customer"),
    # manager
    path('statistics', StatisticsView.as_view(), name="statistics"),
    path('manageInventory', ManageInventory.as_view(), name="manageInventory"),
    path('manageInventory/<str:category_name>/', ManageInventory.as_view(), name='manageInvenCat'),
    path('editProduct/<int:product_id>/', Editproduct.as_view(), name="editProduct"),
    path('deleteProduct/<int:product_id>/', DeleteProduct.as_view(), name='delete_product'),
    path('addProduct/', AddProduct.as_view(), name='addProduct'),
    # path('ManageUser/', ManageUserView.as_view(), name="ManageUser"),
    path('employee/', EmployeeList.as_view(), name='employee-list'),
    path('employee/new/', CreateEmployee.as_view(), name='employee-create'),
    path('employee/<int:emp_id>/', ManageEmployee.as_view(), name='employee-edit'),

]