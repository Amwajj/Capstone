from django import forms
from .models import RiderRequest

class RiderRequestForm(forms.ModelForm):
    class Meta:
        model = RiderRequest
        fields = [
            'city','days_of_week','start_neighborhood',
            'end_neighborhood','start_time','end_time','start_date','end_date',
            'total_riders','price'
        ]