from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from riders.models import Rider
from drivers.models import Driver
from django.contrib import messages
from drivers.forms import DriverForm
from drivers.models import Car, CarCompany
# Create your views here.

def sign_up_rider(request: HttpRequest):
    """تسجيل راكب جديد"""
    
    if request.method == 'POST':
        # بيانات الحساب
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        
        # Validations
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:sign_up_rider')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.', "alert-warning")
            return redirect('accounts:sign_up_rider')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.', "alert-warning")
            return redirect('accounts:sign_up_rider')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.', "alert-warning")
            return redirect('accounts:sign_up_rider')
        
        # إنشاء User
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # إنشاء Rider (بدون بيانات إضافية الآن)
        Rider.objects.create(user=user)
        
        login(request, user)
        messages.success(request, f'Welcome {username}! You are registered as a Rider.')
        return redirect('main:home_view')
    
    return render(request, 'accounts/signup_rider.html')


def sign_up_driver(request: HttpRequest):
    """تسجيل سائق جديد"""
    
    if request.method == 'POST':
        # بيانات الحساب
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        
        # Validations
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.', "alert-warning")
            return redirect('accounts:sign_up_driver')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.', "alert-warning")
            return redirect('accounts:sign_up_driver')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.', "alert-warning")
            return redirect('accounts:sign_up_driver')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.', "alert-warning")
            return redirect('accounts:sign_up_driver')
        
        # إنشاء User
        user = User.objects.create_user(username=username, password=password, email=email)
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        
        # إنشاء Driver باستخدام الفورم
        driver_form = DriverForm(request.POST, request.FILES)
        if driver_form.is_valid():
            driver = driver_form.save(commit=False)
            driver.user = user
            driver.status = 'PENDING'
            
            # إذا رفع السائق صورة الاستمارة، ننشئ Car object
            car_registration_file = request.FILES.get('car_registration')
            if car_registration_file:
                # نستخدم شركة افتراضية (ننشئها لو ما موجودة)
                unknown_company, _ = CarCompany.objects.get_or_create(name="Unknown")
                car = Car.objects.create(
                    company=unknown_company,  # مؤقت - بعدين يعدلها من البروفايل
                    model='Pending',
                    year=None,
                    color='',
                    plate_number='',
                    seats_count=None,
                    car_registration=car_registration_file
                )
                driver.car = car
            
            driver.save()
            driver_form.save_m2m()  # حفظ ManyToMany fields (cities)
        else:
            print("❌ Driver form errors:", driver_form.errors)
            messages.error(request, "Driver information is invalid.")
            user.delete()  # مهم عشان ما يننشأ User بدون Driver
            return redirect('accounts:sign_up_driver')
        
        login(request, user)
        messages.success(request, f'Welcome {username}! You are registered as a Driver. Your account is pending approval.', "alert-info")

        return redirect('main:home_view')
    
    # GET request
    form = DriverForm()
    return render(request, 'accounts/signup_driver.html', {'form': form})

def sign_in(request: HttpRequest):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:profile_view')
        else:
            messages.error(request, 'Invalid username or password.', "alert-danger")
            return redirect('accounts:sign_in')
    
    return render(request, 'accounts/signin.html')

def log_out(request: HttpRequest):

    logout(request)
    messages.success(request, 'You have been logged out.', "alert-warning")

    return redirect('main:home_view')

