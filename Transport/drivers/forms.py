from django import forms
from .models import Driver

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        exclude = ['user', 'status']  # استثناء user و status
        
        # Labels
        labels = {
            'phone': 'Phone Number',
            'national_id_or_iqama': 'National ID / Iqama',
            'gender': 'Gender',
            'avatar': 'Profile Picture',
            'date_of_birth': 'Date of Birth',
            'city': 'Cities',
            'licenses': 'Driving License',
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
            'car': forms.Select(attrs={
                'class': 'form-select'
            }),
            'city': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
        }
        
        # help texts
        help_texts = {
            'phone': 'Format: 9665xxxxxxxx or 05xxxxxxxx',
            'city': 'Hold Ctrl/Cmd to select multiple cities',
        }