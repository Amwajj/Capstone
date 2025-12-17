from django.contrib import admin
from .models import City, Neighborhood,Day,Contact

# Register your models here.
admin.site.register(City)
admin.site.register(Neighborhood)
admin.site.register(Day)
admin.site.register(Contact)