from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(user)
admin.site.register(collection)
admin.site.register(movie)