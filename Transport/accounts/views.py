from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from trip_subscription.models import TripSubscription
from riders.models import Rider
from drivers.models import Driver
from django.contrib import messages
from drivers.forms import DriverForm
from riders.forms import RiderForm
from drivers.models import Car, CarCompany
from main.models import City, Nationality
from trips.models import Trip, JoinTrip
from django.contrib.auth.decorators import login_required
from django.db import transaction  
from django.utils.http import url_has_allowed_host_and_scheme  
from django.contrib import messages

from django.db.models import Count, Q


#  Helper لتقليل التكرار 
def _render_rider_signup(request, form):
    cities = City.objects.all()
    return render(
        request,
        'accounts/signup_rider.html',
        {
            'form': form,
            'cities': cities
        }
    )


def sign_up_rider(request: HttpRequest):
    """تسجيل راكب جديد"""


    if request.method == 'POST':
        # بيانات الحساب
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')

        rider_form = RiderForm(request.POST, request.FILES)


        # Validations 
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return _render_rider_signup(request, rider_form)
          


        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return _render_rider_signup(request, rider_form)
          

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return _render_rider_signup(request, rider_form)
           

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return _render_rider_signup(request, rider_form)
         


        try:  
            with transaction.atomic():  
                # إنشاء User 
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=request.POST.get('first_name', ''),
                    last_name=request.POST.get('last_name', '')
                )

                # إنشاء Rider باستخدام الفورم
                if rider_form.is_valid():
                    rider = rider_form.save(commit=False)
                    rider.user = user
                    rider.save()
                else:
                    #   بالحذف لكن بدون حذف يدوي زي الي سويته قبل — transaction يتكفّل
                    print("❌ Rider form errors:", rider_form.errors)
                    messages.error(request, "Rider information is invalid.")
                    raise ValueError("Invalid rider form")  

        except ValueError:
            # أخطاء الفورم - نرجّع نفس الصفحة مع البيانات
            return _render_rider_signup(request, rider_form) 

        except Exception:
            # خطأ غير متوقع - صفحة 403 الخاصة في موقعنا
            return render(request, '403.html', status=403)  

        login(request, user)
        messages.success(
            request,
            f'Welcome {username}! You are registered as a Rider.'
        )
        return redirect('accounts:sign_in')  

    # GET
    form = RiderForm()
    cities = City.objects.all()
    return render(request, 'accounts/signup_rider.html', {'form': form, 'cities': cities})

def _render_driver_signup(request, form):
    cities = City.objects.all()
    nationalities = Nationality.objects.all()
    return render(
        request,
        'accounts/signup_driver.html',
        {
            'form': form,
            'cities': cities,
            'nationalities': nationalities
        }
    )

def sign_up_driver(request: HttpRequest):
    """تسجيل سائق جديد"""


    if request.method == 'POST':
        # بيانات الحساب
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')

        driver_form = DriverForm(request.POST, request.FILES)


        # Validations 
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.', "alert-warning")
            return _render_driver_signup(request, driver_form)

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.', "alert-warning")
            return _render_driver_signup(request, driver_form)

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.', "alert-warning")
            return _render_driver_signup(request, driver_form)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.', "alert-warning")
            return _render_driver_signup(request, driver_form)


        try:  # ⭐
            with transaction.atomic():  # ⭐
                # إنشاء User (كما هو)
                user = User.objects.create_user(username=username, password=password, email=email)
                user.first_name = request.POST.get('first_name', '')
                user.last_name = request.POST.get('last_name', '')
                user.save()

                # إنشاء Driver باستخدام الفورم
                if driver_form.is_valid():
                    driver = driver_form.save(commit=False)
                    driver.user = user
                    driver.status = 'PENDING'
                    driver.save()
                else:
                    print("❌ Driver form errors:", driver_form.errors)
                    messages.error(request, "Driver information is invalid.")
                    raise ValueError("Invalid driver form")  # ⭐

        except ValueError:
            # أخطاء الفورم - نرجّع نفس الصفحة مع البيانات
            return _render_driver_signup(request, driver_form)

        except Exception:
            # أي خطأ غير متوقع
            return render(request, '403.html', status=403)  # ⭐

        login(request, user)
        messages.success(
            request,
            f'Welcome {username}! You are registered as a Driver. Your account is pending approval.',
            "alert-info"
        )
        return redirect('accounts:sign_in')  



    # GET request
    form = DriverForm()
    return _render_driver_signup(request, form)



def sign_in(request: HttpRequest):

    next_url = request.GET.get("next") or request.POST.get("next")  


    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

    # ⭐ حماية من open redirect
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)  # ⭐

            return redirect("main:home_view")  # ⭐
        
        else:
            messages.error(request, 'Invalid username or password.', "alert-danger")
            return render(request, 'accounts/signin.html')

    return render(request, 'accounts/signin.html')


def log_out(request: HttpRequest):

    next_url = request.GET.get('next')  # ⭐
    logout(request)
    messages.success(request, 'You have been logged out.', "alert-warning")
    return redirect(next_url or 'main:home_view')  # ⭐


@login_required
def profile_driver(request: HttpRequest, driver_id=None):
    try:
        if driver_id:
            driver = Driver.objects.get(id=driver_id)
        else:
            driver = request.user.driver
    except Driver.DoesNotExist:
        return render(request, '404.html', status=404)  # ⭐
    except AttributeError:
        return render(request, '403.html', status=403)  # ⭐
 
    car = driver.car if hasattr(driver, 'car') else None
    # جلب جميع الرحلات التي أنشأها السائق
    trips = driver.trips.all().order_by('-created_at')

    subscriptions = driver.trips.filter(
    admin_status='APPROVED'
    ).annotate(
    subscribed_count=Count(
        'jointrip',  
        filter=Q(jointrip__rider_status='APPROVED')
    )
    ).order_by('-created_at')
    return render(request, 'accounts/profile_driver.html', {'driver': driver, 'car': car, 'trips': trips,'subscriptions':subscriptions})


@login_required
def edit_driver_profile(request: HttpRequest):
    """تعديل بروفايل السائق"""
    driver = request.user.driver

    if request.method == 'POST':
        driver_form = DriverForm(request.POST, request.FILES, instance=driver)
        if driver_form.is_valid():
            driver_form.save()
            messages.success(request, 'Profile updated successfully!', "alert-success")
            return redirect("accounts:profile_driver", driver_id=driver.id)
        else:
            messages.error(request, 'Please correct the errors below.', "alert-danger")
    else:
        driver_form = DriverForm(instance=driver)

    cities = City.objects.all()
    nationalities = Nationality.objects.all()

    return render(
        request,
        'accounts/edit_driver_profile.html',
        {'driver': driver, 'form': driver_form, 'cities': cities, 'nationalities': nationalities}
    )


@login_required
def profile_rider(request: HttpRequest, rider_id=None):
    try:
        if rider_id:
            rider = Rider.objects.select_related('user').get(id=rider_id)
        else:
            rider = request.user.rider
    except Rider.DoesNotExist:
        return render(request, '404.html', status=404)  # ⭐
    except AttributeError:
        return render(request, '403.html', status=403)  # ⭐

    joined_trips = JoinTrip.objects.select_related(
            'trip',
            'trip__driver',
            'trip__city'
        ).filter(
            rider=rider
        ).order_by('-created_at')
    
    subscriptions = TripSubscription.objects.filter(
            rider=rider
        ).values_list('join_trip_id', flat=True)
    
    
    has_rejected = joined_trips.filter(rider_status='REJECTED').exists()
    if has_rejected:
        messages.warning(request, "Attention: You have rejected join requests. Please check the details in your joined trips list.")
    return render(request, 'accounts/profile_rider.html', {'rider': rider,'has_rejected':has_rejected, 'subscriptions':subscriptions, 'joined_trips':joined_trips})

@login_required
def edit_rider_profile(request: HttpRequest):
    """تعديل بروفايل الراكب"""
    rider = request.user.rider

    if request.method == 'POST':
        rider_form = RiderForm(request.POST, request.FILES, instance=rider)
        if rider_form.is_valid():
            rider_form.save()
            messages.success(request, 'Profile updated successfully!', "alert-success")
            return redirect('accounts:profile_rider')
        else:
            messages.error(request, 'Please correct the errors below.', "alert-danger")
    else:
        rider_form = RiderForm(instance=rider)

    cities = City.objects.all()

    return render(
        request,
        'accounts/edit_rider_profile.html',
        {'rider': rider, 'form': rider_form, 'cities': cities}
    )
