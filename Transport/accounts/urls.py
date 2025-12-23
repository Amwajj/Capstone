from django.urls import path
from . import views

app_name = "accounts"

urlpatterns=[
    path('signup/rider/', views.sign_up_rider, name='sign_up_rider'),
    path('signup/driver/', views.sign_up_driver, name='sign_up_driver'),
    path('signin/', views.sign_in, name='sign_in'),
    path("login/", views.sign_in),  #  يخلي /accounts/login/ يشتغل
    path('logout/', views.log_out, name='log_out'),
    path('profile/driver/edit/', views.edit_driver_profile, name='edit_driver_profile'),
    path('profile/driver/<int:driver_id>', views.profile_driver, name='profile_driver'),
    path('profile/rider/edit/', views.edit_rider_profile, name='edit_rider_profile'),
    path('profile/rider/<int:rider_id>', views.profile_rider, name='profile_rider'),
]