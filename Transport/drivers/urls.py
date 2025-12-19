from django.urls import path

from . import views


app_name = "drivers"


urlpatterns=[
    path("car/", views.driver_car_view, name="driver_car"),

]