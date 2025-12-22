from django.shortcuts import render, redirect
from django.http import HttpRequest

#for messages notifications
from django.contrib import messages

#for Pagination
from django.core.paginator import Paginator

#for sending email message
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

#for authentications (superuser)
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST


from rider_request.models import RiderRequest
from main.models import Contact
from drivers.models import Driver
from trips.models import Trip
from main.models import City


# Create your views here.

def home_view(request:HttpRequest):

    new_rider_request_ads = RiderRequest.objects.all().order_by('-id')
    rider_requests = new_rider_request_ads[:4]

    drivers_count = Driver.objects.count()
    trips_count = Trip.objects.count()
    cities_count = City.objects.count()

    return render(request, "main/home.html", {
        "rider_requests": rider_requests,
        "drivers_count": drivers_count,
        "trips_count": trips_count,
        "cities_count": cities_count,
    })

#Contact view
def contact_view(request:HttpRequest):

    if request.method == "POST":
        new_msg = Contact( first_name = request.POST["first_name"], last_name = request.POST["last_name"], email = request.POST["email"], message = request.POST["message"])
        new_msg.save()  

        #send confirmation email
        content_html = render_to_string ("main/mail/configration.html")
        send_to = new_msg.email
        email_message = EmailMessage("Message sending confirmation",  content_html, settings.EMAIL_HOST_USER, {send_to})
        email_message.content_subtype = "html"

        email_message.send()          

        messages.success(request, "The message sends successfully", "alert-success")

    return render(request, "main/contact.html")

#Contact message view
def contact_message_view(request:HttpRequest):

    msg = Contact.objects.all().order_by("-created_at")

    return render(request, "main/message.html", {"msg":msg})


# About Us view
def about_view(request: HttpRequest):
    return render(request, "main/about.html")


#Admin view
def manager_view(request: HttpRequest):

    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied: You do not have the required permissions to view this page.")
    
    if request.method == "POST":
        action = request.POST.get('action')
        driver_id = request.POST.get('driver_id')
        trip_id = request.POST.get('trip_id')
        
        if driver_id:
            driver = get_object_or_404(Driver, id=driver_id)
            
            if action == "approve":
                driver.status = 'APPROVED'
                driver.save()
                messages.success(request, f"Driver {driver.user.username} approved successfully!")
            elif action == "reject":
                driver.status = 'REJECTED'
                driver.save()
                messages.error(request, f"Driver {driver.user.username} has been rejected.")
        
        elif trip_id:
            trip = get_object_or_404(Trip, id=trip_id)
            if action == "approve":
                trip.admin_status = 'APPROVED'
                messages.success(request, f"Trip #{trip.id} approved!")
            elif action == "reject":
                trip.admin_status = 'REJECTED'
                messages.error(request, f"Trip #{trip.id} rejected.")
            trip.save()    
        

        return redirect('main:manager_view') 

    driver_list = Driver.objects.filter(status='PENDING')
    trip_list = Trip.objects.filter(admin_status = 'PENDING')

    #Driver Pagination
    paginator_drivers = Paginator(driver_list, 7)
    page_number_drivers = request.GET.get('page_drivers')
    drivers_page_obj = paginator_drivers.get_page(page_number_drivers)

    #Trip Pagination
    paginator_trips = Paginator(trip_list, 7)
    page_number_trips = request.GET.get('page_trips')
    trips_page_obj = paginator_trips.get_page(page_number_trips)

    return render(request, "main/manager.html", {"drivers": drivers_page_obj, "trips": trips_page_obj})


