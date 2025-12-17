
from django.contrib import admin
from .models import Driver, Car, CarCompany

# Register your models here.

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'gender', 'status', 'date_of_birth']
    list_filter = ['status', 'gender']
    search_fields = ['user__username', 'phone', 'national_id_or_iqama']
    list_editable = ['status']  # يمكنك تغيير الحالة مباشرة من القائمة
    readonly_fields = ['user']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'status')
        }),
        ('Personal Information', {
            'fields': ('phone', 'national_id_or_iqama', 'gender', 'date_of_birth', 'avatar')
        }),
        ('Driver Details', {
            'fields': ('licenses', 'car', 'city')
        }),
    )

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['model', 'company', 'year', 'color', 'plate_number', 'seats_count']
    list_filter = ['company', 'year']
    search_fields = ['model', 'plate_number']

@admin.register(CarCompany)
class CarCompanyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']