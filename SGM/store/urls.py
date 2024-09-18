from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', Inventory.as_view(), name="inventory"),
    path('ManageUser', ManageUserView.as_view(), name="ManageUser"),
]
