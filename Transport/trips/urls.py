from django.urls import path

from . import views


app_name = "trips"


urlpatterns=[
path('all/', views.all_trip_view, name='all_trip_view'),
path('detail/<int:trip_id>/', views.trip_detail_view, name='trip_detail_view'),
path('create/', views.create_trip_view, name='create_trip_view'),
path('update/<int:trip_id>/', views.update_trip_view, name='update_trip_view'),
path('delete/<int:trip_id>/', views.delete_trip_view, name='delete_trip_view'),
]