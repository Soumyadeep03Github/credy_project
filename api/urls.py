from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('register/',views.register_user, name='register_user'),
    path('login/',views.login_user, name='login_user'),
    path('movies/',views.movies, name='movies'),
    path('collection/',views.all_collection, name='collection'),
    path('collection/<collection_uuid>/',views.selected_collection, name='collection_selected'),
    path('request-count/',views.request_count, name='request-count'),
    path('request-count/reset/',views.reset_count, name='reset_count'),
]