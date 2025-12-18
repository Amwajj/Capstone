from django.db import models
from django.contrib.auth.models import User
from riders.models import Rider
from trips.models import Trip
from main.models import Neighborhood
from main.models import City
from main.models import Day

# Create your models here.

class RiderRequest (models.Model):

    class Status (models.TextChoices):
        A = "accept", "Accept"
        R = "reject", "Reject"

    rider = models.ForeignKey(Rider, on_delete= models.CASCADE)
    accepted_trip = models.ForeignKey(Trip, on_delete= models.CASCADE)
    city = models.ForeignKey(City, on_delete= models.CASCADE)
    days_of_week = models.ManyToManyField(Day)
    start_neighborhood = models.ManyToManyField(Neighborhood, related_name="rider_starts")
    end_neighborhood = models.ManyToManyField(Neighborhood, related_name="rider_ends")
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_riders = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.R)
    

class CommentRiderRequest (models.Model):

    user = models.ForeignKey(User, on_delete= models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rider_request = models.ForeignKey(RiderRequest, on_delete= models.CASCADE)