from django.db import models
from django.contrib.auth.models import User
from main.models import City
from drivers.models import Driver
from django.core.validators import RegexValidator



# Create your models here.

class Rider (models.Model):

    #validator Phone
    phone_regex = RegexValidator(
        regex=r'^(9665\d{8}|05\d{8})$',
        message="Phone number must be in format: '9665********' or '05********' (10 digits). Only digits allowed."
    )
    #Gender
    class Gender (models.TextChoices):
        F = "female", "Female"
        M = "male", "Male"

    #Car size
    class SizeCarName (models.TextChoices):
        S = "small", "Small"
        M = "medium", "Medium"
        L = "larg", "Larg"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    national_id_or_iqama = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=6, choices=Gender.choices, default=Gender.F)
    avatar = models.ImageField(upload_to="images/avatars/",default="images/avatars/avatar.webp")
    date_of_birth = models.DateField()

    size_car = models.CharField(max_length=64, choices=SizeCarName.choices, default=SizeCarName.M)
    cities = models.ManyToManyField(City)

class ReviewRider (models.Model):
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver,on_delete=models.CASCADE)
    rating = models.SmallIntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)