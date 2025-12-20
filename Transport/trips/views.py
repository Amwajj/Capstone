from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest

from .models import Trip ,JoinTrip
from drivers.models import Driver
from riders.models import Rider
from .forms import TripForm, JoinTripForm
from main.models import City, Neighborhood, Day
from django.db.models import Q
# Create your views here.
def all_trip_view(request:HttpRequest):
    trips =Trip.objects.filter(admin_status='APPROVED')
    if request.user.is_authenticated:
        try:
            ride_city = request.user.rider.city
            trips =Trip.objects.filter(city=ride_city, admin_status='APPROVED')# يطلع الرحلات على حسب مدينة الراكب
        except AttributeError:
            pass

        search = request.GET.get('search')
        if search:
            trips = trips.filter(
                Q(start_neighborhood__name__icontains=search) |
            Q(end_neighborhood__name__icontains=search)
            )
    start_neighborhoods = request.GET.getlist('start_neighborhood')
    if start_neighborhoods:
        trips = trips.filter(start_neighborhood__id__in=start_neighborhoods)


    end_neighborhoods = request.GET.getlist('end_neighborhood')
    if end_neighborhoods:
        trips = trips.filter(end_neighborhood__id__in=end_neighborhoods)
       
        start_date = request.GET.get('start_date')
        if start_date:
            trips= trips.filter(start_date__gte=start_date)

        end_date = request.GET.get('end_date')
        if end_date:
            trips= trips.filter(end_date__lte=end_date)
        
        trips = trips.distinct()
 

    return render(request, 'trips/trips_list.html',{'trips':trips})


def trip_detail_view(request:HttpRequest, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, admin_status='APPROVED')

    driver = trip.driver
    car = driver.car

    context = {
        'trip':trip,
        'driver':driver,
        'car': car
    }
    return render(request, 'trips/trip_detail.html',context)

@login_required
def create_trip_view(request:HttpRequest):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, "Must be driver to create trip")
        return redirect('accounts:sign_in')


    if driver.status != 'APPROVED':
        messages.error(
            request,
            "Your account is under review. You can create trips only after admin approval."
        )
        return redirect('accounts:profile_driver')
    
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.driver = driver
            trip.save()
            form.save_m2m()
            messages.success(request, "Created Trip successfully", "alert-success")
            return redirect('main:home_view')
        else:
            messages.error(request, "Please correct the errors below.", "alert-danger")

    else:
        form = TripForm()

    context = {
        'form':form,
        'cities': City.objects.all(),
        'neighborhoods': Neighborhood.objects.all(),
        'days': Day.objects.all(),
    }

    return render(request, "trips/create_trip.html",context) 

@login_required
def update_trip_view(request:HttpRequest , trip_id):

    trip=get_object_or_404(Trip, id=trip_id)
         
    if trip.driver.user != request.user:
        messages.error(request, "You are not allowed to edit this trip")
        return redirect('main:home_view')
    
    if request.method =="POST":
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            messages.success(request, "Trip updated successfully")
            return redirect('trips:trip_detail_view', trip_id=trip_id)
    else:
        form = TripForm(instance=trip)

    context = {
        'cities': City.objects.all(),
        'neighborhoods': Neighborhood.objects.all(),
        'days': Day.objects.all(),
    }
    return render(request, "trips/update_trip.html",context) 

@login_required
def delete_trip_view(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if trip.driver.user != request.user:
        messages.error(request, "You are not allowed to delete this trip", "alert-warning")
        return redirect('trips:trip_detail_view', trip_id=trip_id)

    if request.method == "POST":
        try:
            trip.delete()
            messages.success(request, "Trip deleted successfully")
        except Exception as e:
             messages.error(request, f"Error: {e}", "alert-danger")

    return redirect("accounts:profile_driver")


@login_required
def join_trip_view(request:HttpRequest, trip_id):
    try:
        rider = request.user.rider
    except Rider.DoesNotExist:
        messages.error(request, "Only riders can join trips.")
        return redirect('trips:trip_detail_view', trip_id=trip.id)


    trip = get_object_or_404(Trip, id= trip_id)

    if JoinTrip.objects.filter(trip=trip, rider= rider).exists():
        messages.warning(request, "You have already requested to join this trip.","alert-warning")
        return redirect('trips:trip_detail_view', trip_id=trip.id)
    
    if request.method == "POST":
        form = JoinTripForm(request.POST)
        if form.is_valid():
            join_req = form.save(commit=False)
            join_req.trip = trip
            join_req.rider = rider
            join_req.save()
            messages.success(request, "Your request to join the tip has been sent!", "alert-success")
        else:
            messages.error(request, "Please correct the errors below.", "alert-danger")
        
    return redirect('trips:trip_detail_view', trip_id=trip.id)

 

