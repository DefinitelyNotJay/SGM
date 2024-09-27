from django.contrib import admin
from django.urls import path, include
from django.http import *
from .views import *

urlpatterns = [
    path('Viewproduct', ViewStock.as_view(), name="Viewproduct"),
]

