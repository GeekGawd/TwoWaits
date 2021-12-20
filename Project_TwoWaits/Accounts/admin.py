from django.contrib import admin
from .models import OTP, UserAccount
# Register your models here.
admin.site.register(UserAccount)
admin.site.register(OTP)
