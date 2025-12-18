from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import Trip

# Register your models here.


class TripAdmin(admin.ModelAdmin):
    list_display = ['driver', 'start_date', 'end_date', 'price']
    list_filter = ['start_neighborhood', 'end_neighborhood']


admin.site.register(Trip, TripAdmin)

