from django.urls import path
from .views import *

app_name = "dashboard"

urlpatterns = [
    path("", index, name="index"),
    path("posts/", posts, name="posts"),
    path("following/", following, name="following"),
    path("followers/", followers, name="followers"),
    path("tags/", tags, name="tags"),
    path("bookmarks/", bookmarks, name="bookmarks"),
    path("analytics/", analytics, name="analytics"),
    # --- Settings ---
    path("settings/profile/", profile, name="profile_settings"),
    path("settings/security/", security, name="security_settings"),
    path("terminate-sessions/", terminate_sessions, name="terminate_sessions"),
    path("terminate-session/<str:session_key>/", delete_session, name="delete_session"),
    path("settings/email/", email_settings, name="email_settings"),
]
