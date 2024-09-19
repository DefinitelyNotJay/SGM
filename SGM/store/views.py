from django.shortcuts import render
from django.views import View
from django.http import *
from store.models import *
from .forms.authentication import *
from .forms.customer import *
# Create your views here.

class Inventory(View):
    def get(self, request):
        return render(request, "registration/add_customer.html", {"form": CustomerCreateForm()})

class SignUp(View):
    def get(self, request):
        return render(request, "registration/sign_up.html", {"form": RegisterForm()})