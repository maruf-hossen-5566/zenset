from django.contrib import admin

from profile_app.models import Follow

# Register your models here.
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'follower', 'created_at')
    search_fields = ('user__username', 'follower__username')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
