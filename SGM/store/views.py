from django.shortcuts import render, redirect
from django.views import View
from django.http import *
from store.models import *
from .forms.authentication import *
from .forms.customer import *
from django.forms.models import model_to_dict
# Create your views here.

class Inventory(View):
    def get(self, request):
        return render(request, "employee/customer_form.html", {"form": CustomerCreateForm()})

class SignUp(View):
    def get(self, request):
        return render(request, "registration/sign_up.html", {"form": RegisterForm()})

class ManageCustomer(View):
    def get(self, request, customer_id=None):
        if(customer_id):
            # edit customer info
            customer_instance = Customer.objects.get(pk=customer_id)
            edit_form = CustomerCreateForm(initial=model_to_dict(customer_instance), instance=customer_instance)
            context = {"form": edit_form, "customer": customer_instance}
            return render(request, "employee/customer_form.html", context)

        # get all customers
        customers = Customer.objects.all()
        return render(request, "employee/all_customer.html", {"customers": customers})

    def post(self, request, customer_id=None):
        if customer_id:
            customer_instance = Customer.objects.get(pk=customer_id)
            form = CustomerCreateForm(request.POST, instance=customer_instance)
            if form.is_valid:
                try:
                    form.save()
                    return redirect("/customer")
                except:
                    return HttpResponseServerError()
        # create customer
        form = CustomerCreateForm(request.POST)
        if form.is_valid:
            try:
                customer = form.save()
                return redirect("/customer")
            except:
                return redirect("/customer/new/")
        return redirect("/customer")

    def delete(self, request, customer_id):
        print(customer_id)
        return JsonResponse({"success": True})