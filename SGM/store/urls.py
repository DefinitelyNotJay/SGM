from django.contrib import admin
from django.urls import path, include
from django.http import *
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    # all
    path("", include('authen.urls')),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="users_hub/password_reset.html"), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name="users_hub/password_reset_done.html"), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users_hub/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users_hub/password_reset_complete.html'), name='password_reset_complete'),

    # customer
    path('', ViewStock.as_view(), name="view-product"),
    
    # employee
    path('payment/', Payment.as_view()),
    path('payment/bill', PaymentBill.as_view()),
    path('payment/generate-qrcode', GenerateQRCode.as_view(), name='generate_qrcode'),
    path('customer/', CustomerList.as_view(), name="customer-list"),
    path('customer/new/', CreateCustomer.as_view(), name="new-customer"),
    path('customer/<int:customer_id>/', ManageCustomer.as_view(), name="edit-customer"),
    path('customer/viewpoint/',  Viewpoint.as_view(), name="viewpoint"),

    # manager
    path('stock/', Stock.as_view()),
    path('statistics', StatisticsView.as_view(), name="statistics"),
    path('manageInventory', ManageInventory.as_view(), name="manageInventory"),
    path('manageInventory/<str:category_name>/', ManageInventory.as_view(), name='manageInvenCat'),
    path('editProduct/<int:product_id>/', Editproduct.as_view(), name="editProduct"),
    path('deleteProduct/<int:product_id>/', DeleteProduct.as_view(), name='delete_product'),
    path('addProduct/', AddProduct.as_view(), name='addProduct'),  
    path('manageCategories/', ManageCategories.as_view(), name='manageCategories'),
    path('addCategory/', AddCategory.as_view(), name='addCategory'),
    path('editCategory/<int:pk>/', EditCategory.as_view(), name='editCategory'),
    path('deleteCategory/<int:pk>/', DeleteCategory.as_view(), name='deleteCategory'),

    path('employee/', EmployeeList.as_view(), name='employee-list'),
    path('employee/new/', CreateEmployee.as_view(), name='employee-create'),
    path('employee/<int:emp_id>/', ManageEmployee.as_view(), name='employee-edit'),

]