from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blog_app.urls", namespace="blog")),
    path("auth/", include("auth_app.urls", namespace="auth")),
    path("profile/", include("profile_app.urls", namespace="profile")),
    path("dashboard/", include("me_app.urls", namespace="dashboard")),
    path("search/", include("search_app.urls", namespace="search")),
    path("like/", include("like_app.urls", namespace="like")),
    path("comment/", include("comment_app.urls", namespace="comment")),
    path("notification/", include("notification_app.urls", namespace="notify")),
    path("test/", include("test_app.urls", namespace="test")),
    path("", include("user_sessions.urls", "user_sessions")),
    path("contact/", include("contact_app.urls", namespace="contact")),
    path("suggestion/", include("suggestion_app.urls", namespace="suggestion")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    # Only serve media locally during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
