from django.db import models
from riders.models import Rider
from trips.models import JoinTrip
from rider_request.models import JoinRequestTrip

# Create your models here.


class TripSubscription(models.Model):
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    join_trip = models.OneToOneField(JoinTrip, on_delete=models.CASCADE, related_name='subscription')
    join_request_trip = models.OneToOneField(JoinRequestTrip, on_delete=models.CASCADE, null=True, blank=True, related_name='subscription')
    created_at = models.DateTimeField(auto_now_add=True)
    
    

