from django.shortcuts import render
from django.views import View
from django.http import *
from store.models import *
# Create your views here.

class Inventory(View):
    def get(self, request):
        print(Customer.objects.all())
        return HttpResponse("123")