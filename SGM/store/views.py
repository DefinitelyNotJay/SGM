from django.shortcuts import render
from django.views import View
from django.http import *
# Create your views here.

class Inventory(View):
    def get(self, request):
        return HttpResponse("123")