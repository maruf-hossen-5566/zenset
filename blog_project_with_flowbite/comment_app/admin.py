from django.contrib import admin
from comment_app.models import Comment, Reply


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "blog", "user", "content", "reply_count", "created_at", "updated_at")
    search_fields = ("blog__title", "user__username", "content")
    list_filter = ("blog", "user")

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "comment__id", "user", "created_at", "updated_at")
    search_fields = ("comment__content", "user__username", "content")
    list_filter = ("comment", "user")

