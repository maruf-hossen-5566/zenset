from django.urls import path
from . import views

app_name = "search"

urlpatterns = [
    path("", views.search, name="search"),
    path("posts/", views.search_posts, name="search_posts"),
    path("users/", views.search_users, name="search_users"),
    path("tags/", views.search_tags, name="search_tags"),
]
