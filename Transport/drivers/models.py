from django.db import models
from django.contrib.auth.models import User
from main.models import City
from django.core.validators import RegexValidator

# Create your models here.
class CarCompany(models.Model):
    name = models.CharField(max_length=300)

class Car(models.Model):
    company = models.ForeignKey(CarCompany, on_delete=models.CASCADE)
    model = models.CharField(max_length=2048)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=100)
    seats_count = models.PositiveIntegerField()
    car_registration = models.ImageField(upload_to="images/")
    
class Driver (models.Model):
    #status 
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    #validator Phone
    phone_regex = RegexValidator(
        regex=r'^(9665\d{8}|05\d{8})$',
        message="Phone number must be in format: '9665********' or '05********' (10 digits). Only digits allowed."
    )

    #Gender
    class Gender (models.TextChoices):
        F = "female", "Female"
        M = "male", "Male"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    national_id_or_iqama = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=6, choices=Gender.choices, default=Gender.F)
    avatar = models.ImageField(upload_to="images/avatars/",default="images/avatars/avatar.webp")
    date_of_birth = models.DateField(blank=True, null=True)
    cities = models.ManyToManyField(City, blank=True)
    licenses = models.ImageField(upload_to="images/", blank=True, null=True)
    car = models.OneToOneField(Car, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')



class ReviewDriver(models.Model):

    rider = models.ForeignKey('riders.Rider', on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver,on_delete=models.CASCADE)
    rating = models.SmallIntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
