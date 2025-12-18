from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.contrib import messages

from .forms import RiderRequestForm
from .models import RiderRequest
from riders.models import Rider
from main.models import City, Neighborhood, Day



# Create your views here.
def create_rider_request(request:HttpRequest):

    rider_request_form = RiderRequestForm()

    if request.method == "POST":
        rider_request_form = RiderRequestForm(request.POST)
        if rider_request_form.is_valid():
            rider_request_form.save()

            messages.success(request, "Created rider request add successfully", "alert-success")
            return redirect('rider_request:list_rider_request')
        else:
            print("not valid form", rider_request_form.errors)
        
        context = { 'cities':City.objects.all(), 'neighborhoods':Neighborhood.objects.all(), 'days':Day.objects.all()}

    return render(request, "rider_request/rider_request_form.html",{"rider_request_form":rider_request_form, "Status":RiderRequest.Status.choices},context)

def list_rider_request(request:HttpRequest):

    return render(request, "rider_request/rider_request_ads_list.html")

def detail_rider_request(request:HttpRequest):

    return render(request, "rider_request/rider_request_detail.html")

def update_rider_request(request:HttpRequest):

    return render(request, "rider_request/rider_request_update_form.html")