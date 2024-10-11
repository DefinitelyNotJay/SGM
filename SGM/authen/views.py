from django.shortcuts import render
from django.views import View
from store.forms.authentication import *
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group


# Create your views here.

class SignUp(View):
    def get(self, request):
        return render(request, "./registration/sign-up.html", {"form": EmployeeCreateForm()})
    
    def post(self, request):
        form = EmployeeCreateForm(request.POST)
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

class ChangePassword(View):
    def get(self, request):
        password_form = ChangePasswordForm()
        context = {'form': password_form}
        return render(request, 'registration/change-password.html', context)
    def post(self, request):
        form = ChangePasswordForm(request.POST)
        user = User.objects.get(pk=request.user.id)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['old_password']):
                print('why bro')
                form.add_error("old_password", "รหัสผ่านเก่าไม่ถูกต้อง")
                context = {'form': form}
                return render(request, 'registration/change-password.html', context)
            user.set_password(form.cleaned_data['confirm_password'])
            user.save()
        return redirect('/')

        

