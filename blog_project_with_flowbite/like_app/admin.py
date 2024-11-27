from django.contrib import admin

from like_app.models import Like


# Register your models here.
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("blog", "user", "created_at")
    search_fields = ("blog__title", "user__username")
    list_filter = ("blog", "user")
