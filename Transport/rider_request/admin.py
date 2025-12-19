from django.contrib import admin
from .models import RiderRequest, CommentRiderRequest

# Register your models here.
admin.site.register(RiderRequest)
admin.site.register(CommentRiderRequest)