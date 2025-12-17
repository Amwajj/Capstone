from django.shortcuts import render, redirect
from django.http import HttpRequest

#for messages notifications
from django.contrib import messages

from main.models import Contact


# Create your views here.

def home_view(request:HttpRequest):

    return render(request, "main/home.html")

#Contact view
def contact_view(request:HttpRequest):

    if request.method == "POST":
        new_msg = Contact( first_name = request.POST["first_name"], last_name = request.POST["last_name"], email = request.POST["email"], message = request.POST["message"])
        new_msg.save()        
        messages.success(request, "The message sends successfully", "alert-success")

    return render(request, "main/contact.html")

#Contact message view
def contact_message_view(request:HttpRequest):

    msg = Contact.objects.all().order_by("-created_at")

    return render(request, "main/message.html", {"msg":msg})
