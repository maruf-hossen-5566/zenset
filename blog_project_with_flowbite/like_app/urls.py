from django.urls import path
from .views import *

app_name = "like"

urlpatterns = [
    path("<uuid:id>/", like_post, name="like_post"),
]
