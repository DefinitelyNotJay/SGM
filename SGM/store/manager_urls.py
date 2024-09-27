from django.contrib import admin
from django.urls import path, include
from django.http import *
from .views import *

def role_based_urlpatterns(request):
    print(request.user.is_authenticated)
    user = request.user
    if user.is_authenticated:
        return include('')
    
    return HttpResponse("Hey")

urlpatterns = [
    path('', include('.customer_urls')),
    path('', include('.employee_urls')),
    path('statistics', StatisticsView.as_view(), name="statistics"),
    path('manageInventory', ManageInventory.as_view(), name="manageInventory"),
    path('manageInventory/<str:category_name>/', ManageInventory.as_view(), name='manageInvenCat'),
    path('editProduct/<int:product_id>/', Editproduct.as_view(), name="editProduct"),
    path('deleteProduct/<int:product_id>/', DeleteProduct.as_view(), name='delete_product'),
    path('addProduct/', AddProduct.as_view(), name='addProduct'),
    
]

