from django.shortcuts import render
from django.views import View
from store.forms.authentication import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
# Create your views here.

class SignUp(View):
    def get(self, request):
        return render(request, "./registration/sign-up.html", {"form": RegisterForm()})
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(user.is_staff)
            employee_group = Group.objects.get(name='employee')
            manager_group = Group.objects.get(name='manager')
            print(employee_group.id, manager_group.id)
            # add permission group to new create user
            if user.is_staff:
                user.groups.add(employee_group)
            else:
                user.groups.add(manager_group)
            user.save()
            return redirect('/login/')
        return render(request, './registration/sign-up.html', {'form': form})
class SignIn(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
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

