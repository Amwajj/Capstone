from django.urls import path

from . import views


app_name = "main"


urlpatterns=[
    path('',views.home_view,name="home_view"),
    path('contact/',views.contact_view,name="contact_view"),
    path('message/',views.contact_message_view, name="contact_message_view"),
    path('about/', views.about_view, name="about_view"),
    path('manager/',views.manager_view,name="manager_view"),
]