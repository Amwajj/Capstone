from django.urls import path
from . import views

app_name = "rider_request"

urlpatterns = [
    path('create/',views.create_rider_request,name="create_rider_request"),
    path('update/',views.update_rider_request, name="update_rider_request"),
]