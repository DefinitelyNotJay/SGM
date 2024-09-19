from django.shortcuts import render, redirect
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

class ManageCustomer(View):
    def get(self, request):
        customers = Customer.objects.all()
        return HttpResponse(customers)
    def post(self, request):
        form = CustomerCreateForm(request.POST)
        if form.is_valid:
            try:
                customer = form.save()
                return redirect("/")
            except:
                return redirect("/customer/new/")
        return redirect("/customer")