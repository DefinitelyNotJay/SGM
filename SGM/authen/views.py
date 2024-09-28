from django.shortcuts import render
from django.views import View
from store.forms.authentication import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.

class SignUp(View):
    def get(self, request):
        return render(request, "./registration/sign-up.html", {"form": RegisterForm()})
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
        return render(request, './registration/sign-up.html', {'form': form})
class SignIn(View):
    def get(self, request):
        return render(request, './registration/login.html', {'form': AuthenticationForm})

    def post(self, request):
        print(request.POST)
        form = AuthenticationForm(data=request.POST)
        print(form.error_messages)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
        return render(request, './registration/login.html', {"form": form})

class SignOut(View):
    def get(self, request):
        logout(request)
        return redirect('/login')

