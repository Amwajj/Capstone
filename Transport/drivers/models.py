from django.db import models
from django.contrib.auth.models import User
from main.models import City, Nationality
from django.core.validators import RegexValidator

# Create your models here.
class CarCompany(models.Model):
    name = models.CharField(max_length=300)
    
    def __str__(self):
        return self.name

class Car(models.Model):
    company = models.ForeignKey(CarCompany, on_delete=models.CASCADE)
    model = models.CharField(max_length=2048)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=100)
    seats_count = models.PositiveIntegerField()
    car_registration = models.ImageField(upload_to="images/")
    
class Driver (models.Model):
    #rating choices
    class RatingChoices(models.IntegerChoices):
        STAR1 = 1, "One Star"
        STAR2 = 2, "Two Stars"
        STAR3 = 3, "Three Stars"
        STAR4 = 4, "Four Stars"
        STAR5 = 5, "Five Stars"
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

    #fields    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    national_id_or_iqama = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=6, choices=Gender.choices, default=Gender.F)
    avatar = models.ImageField(upload_to="images/avatars/",default="images/avatars/avatar.webp")
    date_of_birth = models.DateField(blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.SET_NULL, blank=True, null=True)
    licenses = models.ImageField(upload_to="images/licenses/", blank=True, null=True)
    car = models.OneToOneField(Car, on_delete=models.CASCADE, blank=True, null=True)

    rating = models.SmallIntegerField(choices=RatingChoices.choices ,default=RatingChoices.STAR5)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')



class ReviewDriver(models.Model):

    rider = models.ForeignKey('riders.Rider', on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver,on_delete=models.CASCADE)
    rating = models.SmallIntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
