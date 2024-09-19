from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', Inventory.as_view(), name="inventory"),
    path('statistics', StatisticsView.as_view(), name="statistics"),
    path('Viewproduct', ViewStock.as_view(), name="Viewproduct"),
]

