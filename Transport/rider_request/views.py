from django.shortcuts import render, redirect
from django.http import HttpRequest

# Create your views here.
def create_rider_request(request:HttpRequest):

    return render(request, "rider_request/rider_request_form.html")

def update_rider_request(request:HttpRequest):

    return render(request, "rider_request/rider_request_update_form.html")