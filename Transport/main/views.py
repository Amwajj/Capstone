from django.shortcuts import render, redirect
from django.http import HttpRequest

#for messages notifications
from django.contrib import messages

#for sending email message
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

#for authentications (superuser)
from django.shortcuts import get_object_or_404, redirect
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

    driver_list = Driver.objects.filter(status = 'PENDING')

    return render(request, "main/manager.html", {"drivers":driver_list})


