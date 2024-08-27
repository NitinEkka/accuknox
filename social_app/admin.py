from django.contrib import admin
from .models import CustomUser, FriendReq
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(FriendReq)