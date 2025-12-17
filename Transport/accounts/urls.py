from django.urls import path
from . import views

app_name = "accounts"

urlpatterns=[
    path('signup/rider/', views.sign_up_rider, name='sign_up_rider'),
    path('signup/driver/', views.sign_up_driver, name='sign_up_driver'),
    path('signin/', views.sign_in, name='sign_in'),
    path('logout/', views.log_out, name='log_out'),
]