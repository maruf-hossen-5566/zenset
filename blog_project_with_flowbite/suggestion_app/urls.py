from django.urls import path
from . import views

app_name = "suggestion"

urlpatterns = [
    path("", views.index, name="index"),
    path("authors/", views.authors, name="writers"),
    path("tags/", views.tags, name="tags"),
]
