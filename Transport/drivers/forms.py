from django import forms
from .models import Driver, Car, CarCompany
from main.models import City, Nationality


class DriverForm(forms.ModelForm):
    # تعريف كل الحقول كإجبارية
    phone = forms.CharField(
        required=True, 
        max_length=17,
        label='Phone Number *',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '9665xxxxxxxx or 05xxxxxxxx'
        })
    )
    national_id_or_iqama = forms.CharField(
        required=True, 
        max_length=20,
        label='National ID / Iqama *',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your ID/Iqama number'
        })
    )
    gender = forms.ChoiceField(
        required=True,
        label='Gender *',
        choices=Driver.Gender.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_of_birth = forms.DateField(
        required=True,
        label='Date of Birth *',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    city = forms.ModelChoiceField(
        required=True,
        label='City *',
        queryset=City.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    nationality = forms.ModelChoiceField(
        required=True,
        label='Nationality *',
        queryset=Nationality.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    licenses = forms.ImageField(
        required=True,
        label='Driving License *',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
   
    class Meta:
        model = Driver
        exclude = ['user', 'status', 'rating', 'car']
        
        # Widgets للحقول المتبقية
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        
        # Labels للحقول المتبقية
        labels = {
            'avatar': 'Profile Picture',
        }




class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = '__all__'
        widgets = {
            'company': forms.Select(attrs={
                'class': 'form-select',
                'id': 'carCompany',
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'carModel',
                'placeholder': 'Enter model name (e.g., Corolla)'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'carYear',
                'placeholder': 'Enter manufacturing year (e.g., 2022)'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'carColor',
                'placeholder': 'Enter car color (e.g., Red, Black)'
            }),
            'plate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'plateNumber',
                'placeholder': 'Enter plate number (e.g., ABC-1234)'
            }),
            'seats_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'seatsCount',
                'placeholder': 'Enter number of seats (e.g., 5)'
            }),
            'car_registration': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'carRegistration',
                'accept': 'images/*',
                'placeholder': 'Upload car registration document (image)'
            }),
        }
