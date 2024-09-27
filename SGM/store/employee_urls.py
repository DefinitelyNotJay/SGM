from django.contrib import admin
from django.urls import path, include
from django.http import *
from .views import *



urlpatterns = [
    path('', include('.customer_urls')),
    path('emp-home', EmployeeHome.as_view()),
    path('stock/', Stock.as_view()),
    path('payment', Payment.as_view()),
    path('payment/bill', PaymentBill.as_view()),
    path('payment/<str:category>', Payment.as_view()),
    path('customer/new/', ManageCustomer.as_view()),
    path('customer/', ListCustomer.as_view(), name="customer"),
    path('customer/<int:customer_id>/', ManageCustomer.as_view(), name="new-customer"),
    
]

