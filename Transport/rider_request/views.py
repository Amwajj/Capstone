from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator

from .forms import RiderRequestForm
from .models import RiderRequest
from riders.models import Rider
from main.models import City, Neighborhood, Day



# Create your views here.

#Create new rider request
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
            rider_request.rider = rider
            rider_request.save()
            rider_request_form.save_m2m()
            messages.success(request, "Created rider request add successfully", "alert-success")
            return redirect('rider_request:list_rider_request')
        else:
            messages.error(request, "Please correct the errors below", "alert-danger")
    else:
        rider_request_form = RiderRequestForm()
        
        context = { 'cities':City.objects.all(), 'neighborhoods':Neighborhood.objects.all(), 
                   'days':Day.objects.all(),"rider_request_form":rider_request_form, "status":RiderRequest.Status.choices}

    return render(request, "rider_request/rider_request_form.html",context)


#Showing the list of rider request ads
def list_rider_request(request:HttpRequest):
    
    rider_requests = RiderRequest.objects.all().order_by('-id') 

    page_number = request.GET.get("page",1)
    paginator = Paginator(rider_requests, 6)
    rider_requests_page =paginator.get_page(page_number)
    
    return render(request, "rider_request/rider_request_ads_list.html", {'rider_requests': rider_requests_page})


#Showing the details of rider request ads
def detail_rider_request(request:HttpRequest,  rider_request_id):

    rider_request = get_object_or_404(RiderRequest, id = rider_request_id)
    rider = rider_request.rider

    return render(request, "rider_request/rider_request_detail.html", {'rider_request':rider_request,'rider':rider })

#update the rider request ads form
@login_required
def update_rider_request(request, pk):
  
    rider_request = get_object_or_404(RiderRequest, pk=pk, rider__user=request.user)
    
    if request.method == "POST":
       
        form = RiderRequestForm(request.POST, instance=rider_request)
        if form.is_valid():
            updated_request = form.save()
            messages.success(request, "The rider request ads updated successfully", "alert-success")
            return redirect('rider_request:list_rider_request')
    else:
      
        form = RiderRequestForm(instance=rider_request)

    context = {
        'rider_request_form': form,
        'rider_request': rider_request,
        'cities': City.objects.all(),
        'neighborhoods': Neighborhood.objects.all(),
        'days': Day.objects.all(),
        'status': RiderRequest.Status.choices
    }
    return render(request, "rider_request/rider_request_update_form.html", context)

@login_required
def delete_rider_request(request, pk):
   
    rider_request = get_object_or_404(RiderRequest, pk=pk, rider__user=request.user)
    
    if request.method == "POST":
        rider_request.delete()
        messages.success(request, "The rider request ads deleted successfully", "alert-success")
        return redirect('rider_request:list_rider_request')
    
    return render(request, "rider_request/rider_request_confirm_delete.html", {'rider_request': rider_request})