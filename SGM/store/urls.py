from django.contrib import admin
from django.urls import path, include
from django.http import *
from .views import *

def role_based_urlpatterns(request):
    return HttpResponse("Hey")

urlpatterns = [
    path('', Inventory.as_view(), name="inventory"),
    path('customer/', ManageCustomer.as_view(), name="customer"),
    path('customer/new/', ManageCustomer.as_view()),
    path('customer/<int:id>/', ManageCustomer.as_view(), name="new-customer"),
    path('sign-up', SignUp.as_view(), name="sign-up")
]
