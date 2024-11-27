from django.urls import path
from .views import *

app_name = "comment"

urlpatterns = [
    path("<id>/", comment_post, name="comment_post"),
    path("delete/<uuid:id>/", comment_delete, name="comment_delete"),
    path("edit/<uuid:id>/", comment_edit, name="comment_edit"),
    path("reply/<uuid:id>/", reply, name="reply"),
    path("reply/edit/<uuid:id>/", reply_edit, name="reply_edit"),
    path("reply/delete/<uuid:id>/", reply_delete, name="reply_delete"),
]
