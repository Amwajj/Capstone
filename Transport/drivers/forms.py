from django import forms
from .models import Driver, Car


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        exclude = ['user', 'status', 'cities']  # استثناء user و status و cities (يتم معالجتها يدوياً)
        
        # Labels
        labels = {
            'phone': 'Phone Number',
            'national_id_or_iqama': 'National ID / Iqama',
            'gender': 'Gender',
            'avatar': 'Profile Picture',
            'date_of_birth': 'Date of Birth',
            'licenses': 'Driving License',
            'car_registration': 'Car Registration (Istimara)',
            'car': 'Car',
        }
        
        # إضافة widgets للتنسيق
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '9665xxxxxxxx or 05xxxxxxxx'
            }),
            'national_id_or_iqama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your ID/Iqama number'
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
            'licenses': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'car_registration': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'car': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cities': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
        }
        
        # help texts
        help_texts = {
            'phone': 'Format: 9665xxxxxxxx or 05xxxxxxxx',
            'cities': 'Hold Ctrl/Cmd to select multiple cities',
            'car_registration': 'Upload a photo of your car registration document',
        }



class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'company',
            'model',
            'year',
            'color',
            'plate_number',
            'seats_count',
            'car_registration',
        ]

        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'plate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'seats_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'car_registration': forms.FileInput(attrs={'class': 'form-control'}),
        }
