from django.shortcuts import render, redirect
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
from rider_request.models import JoinRequestTrip, RiderRequest
from main.models import City, Nationality
from trips.models import Trip, JoinTrip
from rider_request.models import RiderRequest
from django.contrib.auth.decorators import login_required
from django.db import transaction  
from django.utils.http import url_has_allowed_host_and_scheme  
from django.contrib import messages
from django.utils import timezone
from riders.models import ReviewRider
from drivers.models import ReviewDriver

from datetime import date
from django.db.models import Count, Q, Avg


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
        
        if not request.POST.get('accept_terms'):
            messages.error(
                request,
                'You must agree to the Terms & Conditions and Privacy Policy.'
            )
            rider_form = RiderForm(request.POST, request.FILES)
            return _render_rider_signup(request, rider_form)

        
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
        return redirect('main:home_view')  

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

        
        # ✅ تحقق من الموافقة
        if not request.POST.get('accept_terms'):
            messages.error(
                request,
                'You must agree to the Terms & Conditions and Privacy Policy.'
            )
            driver_form = DriverForm(request.POST, request.FILES)
            return _render_driver_signup(request, driver_form)

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


        try:  
            with transaction.atomic():  
                # إنشاء User 
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
                    raise ValueError("Invalid driver form")  

        except ValueError:
            # أخطاء الفورم - نرجّع نفس الصفحة مع البيانات
            return _render_driver_signup(request, driver_form)

        except Exception:
            # أي خطأ غير متوقع
            return render(request, '403.html', status=403)  

        login(request, user)
        messages.success(
            request,
            f'Welcome {username}! You are registered as a Driver. Your account is pending approval.',
            "alert-info"
        )
        return redirect('main:home_view')  



    # GET request
    form = DriverForm()
    cities = City.objects.all()
    nationalities = Nationality.objects.all()
    return render(request, 'accounts/signup_driver.html', { 'form': form, 'cities': cities, 'nationalities': nationalities })




def sign_in(request: HttpRequest):

    next_url = request.GET.get("next") or request.POST.get("next")  


    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back {user.first_name or user.last_name}! You have successfully logged in.", "alert-success")
            #  حماية من open redirect
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)  

            return redirect("main:home_view")  
        
        else:
            messages.error(request, 'Invalid username or password.', "alert-danger")
            return render(
                request,
                'accounts/signin.html',
                {'next': next_url}  
            )

    return render(request, 'accounts/signin.html')


def log_out(request: HttpRequest):

    next_url = request.GET.get('next')  
    logout(request)
    messages.success(request, 'You have been logged out.', "alert-warning")
    return redirect(next_url or 'main:home_view')  


@login_required
def profile_driver(request: HttpRequest, driver_id=None):
    try:
        if driver_id:
            driver = Driver.objects.get(id=driver_id)
        else:
            driver = request.user.driver
    except Driver.DoesNotExist:
        return render(request, '404.html', status=404)  
    except AttributeError:
        return render(request, '403.html', status=403)  
 
    car = driver.car if hasattr(driver, 'car') else None


    received_reviews = ReviewDriver.objects.filter(driver=driver).select_related('rider__user', 'trip').order_by('-created_at')
    #حساب_متوسط_التقييم_لعرضه_تحت_الاسم
    average_rating = received_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
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

    accepted_rider_req = RiderRequest.objects.filter(driver=driver, status=RiderRequest.Status.A)


    today = timezone.now().date()
    expired_trips_exists = driver.trips.filter(end_date__lt=today).exists()
    passengers_to_rate = JoinTrip.objects.filter(trip__driver=driver,rider_status='APPROVED', end_date__lt=today).exclude(
        rider__reviewrider__trip__driver=driver, rider__reviewrider__trip__in=driver.trips.all()).distinct()

    return render(request, 'accounts/profile_driver.html', {'driver': driver, 'car': car, 'trips': trips,'subscriptions':subscriptions, 'accepted_rider_req':accepted_rider_req, 'expired_trips_exists': expired_trips_exists, 'passengers_to_rate': passengers_to_rate,'received_reviews': received_reviews,'average_rating': average_rating,})

#لعملية_تقييم_السائق_للركاب_المنظمين_للرحلة
@login_required
def submit_rider_review(request):
    if request.method == "POST":
        trip_id = request.POST.get('trip_id')
        rider_id = request.POST.get('rider_id')
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')

        try:
            # Ensure the driver is the current user
            driver = request.user.driver
            # Validate that the trip belongs to this driver
            trip = Trip.objects.get(id=trip_id, driver=driver)
            rider = Rider.objects.get(id=rider_id)

            # Create the review record
            ReviewRider.objects.create(
                trip=trip,
                driver=driver,
                rider=rider,
                rating=rating,
                comments=comments
            )
            messages.success(request, "Your rating for the rider has been submitted successfully!")
            
        except Exception as e:
            # You can log 'e' for debugging if needed
            messages.error(request, "An error occurred while saving the rating. Please try again.")
            
    return redirect('accounts:profile_driver', driver_id=driver.id)

@login_required
def edit_driver_profile(request: HttpRequest):
    """تعديل بروفايل السائق"""
    try:
        driver = request.user.driver
    except AttributeError:
        return render(request, '403.html', status=403)  
    
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
        return render(request, '404.html', status=404)  
    except AttributeError:
        return render(request, '403.html', status=403)  

    joined_trips = JoinTrip.objects.select_related(
            'trip',
            'trip__driver',
            'trip__city'
        ).filter(
            rider=rider
        ).order_by('-created_at')
    
    join_requests = JoinRequestTrip.objects.select_related(
        'rider_request',
        'rider_request__driver',
        'rider_request__city'
    ).filter(rider=rider).order_by('-rider_request__start_date')

    owned_requests = JoinRequestTrip.objects.select_related(
        'rider_request',
        'rider_request__driver'
    ).filter(rider_request__rider=rider)
    
    req_trips = (join_requests | owned_requests).distinct()

    subscriptions = TripSubscription.objects.filter(
            rider=rider
        ).values_list('join_trip_id', flat=True)
    
    req_subscriptions = TripSubscription.objects.filter(
        rider=rider
        ).values_list('join_request_trip_id', flat=True)

  
    has_rejected = joined_trips.filter(rider_status='REJECTED').exists()
    
    #rating actions
    today = timezone.now().date()
    received_reviews = ReviewRider.objects.filter(rider=rider).select_related('driver__user', 'trip').order_by('-created_at')
    average_rating = received_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    drivers_to_rate = JoinTrip.objects.filter(
        rider=rider,
        rider_status='APPROVED',
        trip__end_date__lt=today
    ).exclude(
        trip__driver_reviews__rider=rider 
    ).select_related('trip__driver__user')

    context = {'rider': rider,'joined_trips':joined_trips,'has_rejected':has_rejected, 'subscriptions':subscriptions, 'joined_trips':joined_trips,'req_trips':req_trips ,'req_subscriptions':req_subscriptions, 'received_reviews': received_reviews,
        'average_rating': average_rating,
        'drivers_to_rate': drivers_to_rate}
    return render(request, 'accounts/profile_rider.html', context)

#لعملية_تقييم__الراكب_للسائق
@login_required
def submit_driver_review(request):
  
    if request.method == "POST":
        trip_id = request.POST.get('trip_id')
        driver_id = request.POST.get('driver_id')
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')
        rider = request.user.rider 

        try:
           
            ReviewDriver.objects.create(
                trip_id=trip_id,
                driver_id=driver_id,
                rider=rider,
                rating=rating,
                comments=comments
            )
            messages.success(request, "Thank you! Your review for the driver has been submitted successfully.")
            
        except Exception as e:
           
            messages.error(request, "An error occurred while submitting your review. Please try again.")
            print(f"Error: {e}")

 
    return redirect('accounts:profile_rider', rider_id=rider.id)

@login_required
def edit_rider_profile(request: HttpRequest):
    """تعديل بروفايل الراكب"""
    try:
        rider = request.user.rider
    except AttributeError:
        return render(request, '403.html', status=403)  
    
    if request.method == 'POST':
        rider_form = RiderForm(request.POST, request.FILES, instance=rider)
        if rider_form.is_valid():
            rider_form.save()
            messages.success(request, 'Profile updated successfully!', "alert-success")
            return redirect('accounts:profile_rider', rider_id=rider.id)
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
