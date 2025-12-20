from django.db import models
from main.models import City, Neighborhood, Day
from drivers.models import Driver
from riders.models import Rider

# Create your models here.
class Trip (models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="trips")
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()

    start_time = models.TimeField()
    end_time = models.TimeField()

    start_neighborhood = models.ManyToManyField(Neighborhood, related_name="trip_starts")
    end_neighborhood = models.ManyToManyField(Neighborhood, related_name="trip_ends")
    days_of_week = models.ManyToManyField(Day)
    
    total_riders = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    admin_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')


class JoinTrip (models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    comment = models.TextField()
    rider_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    reject_Comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        unique_together = ('trip','rider')