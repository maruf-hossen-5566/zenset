from django.urls import path
from .views import *

app_name = 'profile'

urlpatterns = [
    path('@<str:username>/', profile, name='profile'),
    path('follow/<uuid:user_id>/', follow, name='follow'),
]
