from django.contrib import admin
from notification_app.models import Notification


# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "type", "read", "created_at")
    list_filter = ("type", "read")
    search_fields = ("user__username", "post__title")
    ordering = ("-created_at",)
