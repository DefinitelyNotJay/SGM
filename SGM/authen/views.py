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
        print(form.data)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data.get("password1"))
            employee_group = Group.objects.get(name='employee')
            user.groups.add(employee_group)
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
        print("user", form.get_user())
        print(form.error_messages)
        if form.is_valid():
            # เรียก user หลังจากที่ฟอร์ม valid แล้ว
            user = form.get_user()
            print("user", user)

            # ทำการ login
            login(request, user)
            return redirect('/')
        print(form.errors)  # ใช้ form.errors เพื่อดูข้อความ error ของแต่ละฟิลด์
        form.add_error("password", "เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง")
        return render(request, './registration/login.html', {"form": form})

class SignOut(View):
    def get(self, request):
        logout(request)
        return redirect('/login')

