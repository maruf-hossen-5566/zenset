from django.urls import path
from . import views

app_name = "notify"

urlpatterns = [
    path("", views.index, name="index"),
    # ---
    path("delete/<id>/", views.delete, name="delete"),
    path("clear/", views.delete_all, name="clear"),
]
