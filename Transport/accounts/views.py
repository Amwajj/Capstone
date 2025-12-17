from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest, HttpResponse
from .models import Profile
from riders.models import Rider
from drivers.models import Driver
from django.contrib import messages
from django.contrib.auth.models import User


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
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('accounts:sign_up_rider')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('accounts:sign_up_rider')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('accounts:sign_up_rider')
        
        # إنشاء User
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # إنشاء Profile
        Profile.objects.create(user=user)
        
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
        
        # إنشاء Profile
        Profile.objects.create(user=user)
        
        # إنشاء Driver (بدون بيانات إضافية الآن - status = PENDING)
        Driver.objects.create(user=user, status='PENDING')
        
        login(request, user)
        messages.success(request, f'Welcome {username}! You are registered as a Driver. Your account is pending approval.', "alert-info")
        return redirect('main:home_view')
    
    return render(request, 'accounts/signup_driver.html')

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

def profile_view(request: HttpRequest):
    
    # التحقق من تسجيل الدخول
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to view your profile.', "alert-warning")
        return redirect('accounts:sign_in')
    
    # جلب Profile
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None
    
    # جلب Rider إذا موجود
    try:
        rider = Rider.objects.get(user=request.user)
    except Rider.DoesNotExist:
        rider = None
    
    # جلب Driver إذا موجود
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        driver = None
    
    return render(request, 'accounts/profile.html', {'profile': profile, 'rider': rider, 'driver': driver, })

def update_profile(request: HttpRequest):
    """تحديث الملف الشخصي"""
    
    # التحقق من تسجيل الدخول
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to update your profile.', "alert-warning")
        return redirect('accounts:sign_in')
    
    # التحقق من نوع المستخدم (راكب أو سائق)
    try:
        rider = Rider.objects.get(user=request.user)
        is_rider = True
        is_driver = False
    except Rider.DoesNotExist:
        rider = None
        is_rider = False
    
    try:
        driver = Driver.objects.get(user=request.user)
        is_driver = True
    except Driver.DoesNotExist:
        driver = None
    
    if request.method == 'POST':
        # إذا كان راكب
        if is_rider and rider:
            rider.phone = request.POST.get('phone', '')
            rider.national_id_or_iqama = request.POST.get('national_id_or_iqama', '')
            rider.gender = request.POST.get('gender', 'female')
            rider.date_of_birth = request.POST.get('date_of_birth')
            rider.size_car = request.POST.get('size_car', 'medium')
            
            # تحديث الصورة إذا موجودة
            if request.FILES.get('avatar'):
                rider.avatar = request.FILES['avatar']
            
            rider.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile_view')
        
        # إذا كان سائق
        elif is_driver and driver:
            driver.phone = request.POST.get('phone', '')
            driver.national_id_or_iqama = request.POST.get('national_id_or_iqama', '')
            driver.gender = request.POST.get('gender', 'female')
            driver.date_of_birth = request.POST.get('date_of_birth')
            
            # تحديث الصورة إذا موجودة
            if request.FILES.get('avatar'):
                driver.avatar = request.FILES['avatar']
            
            # تحديث الرخصة إذا موجودة
            if request.FILES.get('licenses'):
                driver.licenses = request.FILES['licenses']
            
            driver.save()
            messages.success(request, 'Profile updated successfully!', "alert-success")
            return redirect('accounts:profile_view')
    
    return render(request, 'accounts/update_profile.html', { 'rider': rider, 'driver': driver, 'is_rider': is_rider, 'is_driver': is_driver, })