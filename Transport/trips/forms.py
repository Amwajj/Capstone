from django import forms
from .models import Trip, JoinTrip

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = [
            'city', 'start_date', 'end_date', 'start_time', 'end_time',
            'start_neighborhood', 'end_neighborhood', 'days_of_week',
            'total_riders', 'price', 'is_private'
        ]


class JoinTripForm(forms.ModelForm):
    class Meta:
        model = JoinTrip
        fields = [
             'start_date', 'end_date', 'comment'
        ]

       