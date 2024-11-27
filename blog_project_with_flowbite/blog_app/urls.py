from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("following/", views.following, name="following"),
    path("Trending/", views.trending, name="trending"),
    path("Latest/", views.latest, name="latest"),
    path("tag/<slug:slug>/", views.tag_detail, name="tag_detail"),
    path("follow-tag/<uuid:id>/", views.follow_tag, name="follow_tag"),
    # --- CRUD Post ---
    path("new-post/", views.create_post, name="create_post"),
    path("new-draft/", views.create_draft_post, name="create_draft_post"),
    path("edit-post/<uuid:id>/", views.edit_post, name="edit_post"),
    path("@<str:username>/<slug:slug>/", views.post_detail, name="post_detail"),
        path("post/delete/<uuid:id>/", views.delete_post, name="delete_post"),
    # --- Post settings ---
    path("bookmark/<uuid:id>/", views.bookmark, name="bookmark"),
    path(
        "change-status/<uuid:id>/", views.change_post_status, name="change_post_status"
    ),
    path(
        "disable-comments/<uuid:id>/", views.disable_comments, name="disable_comments"
    ),

    path("post/delete/<uuid:id>/", views.delete_post, name="delete_post"),
]
