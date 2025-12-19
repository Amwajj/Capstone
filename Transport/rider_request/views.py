from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.contrib import messages

from .forms import RiderRequestForm
from .models import RiderRequest
from riders.models import Rider
from main.models import City, Neighborhood, Day



# Create your views here.
@login_required
def create_rider_request(request:HttpRequest):

    try:
        rider = Rider.objects.get(user=request.user)
    except Rider.DoesNotExist:
        messages.error(request, "Must be rider to create rider request ads")
        return redirect('accounts:sign_in')

    

    if request.method == "POST":
        rider_request_form = RiderRequestForm(request.POST)
        if rider_request_form.is_valid():
            rider_request = rider_request_form.save(commit=False)
            rider_request.rider = request.user.rider
            rider_request.save()
            rider_request_form.save_m2m()
            messages.success(request, "Created rider request add successfully", "alert-success")
            return redirect('rider_request:list_rider_request')
        else:
            messages.error(request, "Please correct the errors below", "alert-danger")
    else:
        rider_request_form = RiderRequestForm()
        
        context = { 'cities':City.objects.all(), 'neighborhoods':Neighborhood.objects.all(), 'days':Day.objects.all(),"rider_request_form":rider_request_form, "status":RiderRequest.Status.choices}

    return render(request, "rider_request/rider_request_form.html",context)

def list_rider_request(request:HttpRequest):

    return render(request, "rider_request/rider_request_ads_list.html")

def detail_rider_request(request:HttpRequest):

    return render(request, "rider_request/rider_request_detail.html")

def update_rider_request(request:HttpRequest):

    return render(request, "rider_request/rider_request_update_form.html")