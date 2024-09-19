from django.contrib import admin
from django.urls import path, include
from django.http import *
from .views import *

def role_based_urlpatterns(request):
    return HttpResponse("Hey")

urlpatterns = [
    path('', Inventory.as_view(), name="inventory"),
    path('sign-up', SignUp.as_view(), name="sign-up")
]
