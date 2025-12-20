from django.urls import path
from . import views

app_name = "rider_request"

urlpatterns = [
    path('create/',views.create_rider_request,name="create_rider_request"),
    path('update/<int:pk>/', views.update_rider_request, name="update_rider_request"),
    path('detail/<int:rider_request_id>/', views.detail_rider_request, name="detail_rider_request"),
    path('list/',views.list_rider_request,name="list_rider_request"),
    path('delete/<int:pk>/', views.delete_rider_request, name="delete_rider_request"),
]