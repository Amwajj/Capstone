from django import forms
from .models import Rider
from main.models import City


class RiderForm(forms.ModelForm):
    class Meta:
        model = Rider
        exclude = ['user']  # user يُربط يدويًا

        # Labels
        labels = {
            'phone': 'Phone Number',
            'national_id_or_iqama': 'National ID / Iqama',
            'gender': 'Gender',
            'avatar': 'Profile Picture',
            'date_of_birth': 'Date of Birth',
            'size_car': 'Preferred Car Size',
            'City': 'City',
        }

        # Widgets
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '9665xxxxxxxx or 05xxxxxxxx'
            }),
            'national_id_or_iqama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your ID / Iqama number'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'size_car': forms.Select(attrs={
                'class': 'form-select'
            }),
            
            'City': forms.Select(attrs={
                'class': 'form-select'
    

            }),
        }

        # Help texts
        help_texts = {
            'phone': 'Format: 9665xxxxxxxx or 05xxxxxxxx',
            'City': 'Select your city from the list',
            'size_car': 'Choose the car size you prefer for your trips',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['City'].queryset = City.objects.all()
