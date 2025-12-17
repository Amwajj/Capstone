from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest

from .models import Trip
from drivers.models import Driver
from .forms import TripForm
from main.models import City, Neighborhood, Day

# Create your views here.
def all_trip_view(request:HttpRequest):
    pass

@login_required
def create_trip_view(request:HttpRequest):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, "Must be driver to create trip")
        return redirect('accounts:sign_in')

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
        form = TripForm()

    context = {
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
            return redirect('main:home_view')
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
    trip=get_object_or_404(Trip, id=trip_id)
         
    if trip.driver.user != request.user:
        messages.error(request, "You are not allowed to delete this trip")
        return redirect('main:home_view')
    
    if request.method =="POST":
        try:
            trip.delete()
            messages.success(request, "Trip delete successfully")

        except Exception as e:
            messages.error(request,"There is a problem. You cannot delete this trip at the moment.", "alert-danger")
    
    return redirect("main:home_view")
