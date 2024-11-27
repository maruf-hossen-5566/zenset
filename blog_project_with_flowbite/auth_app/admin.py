from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'full_name', 'is_staff', 'is_active', "date_joined")
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username', 'full_name', 'image', 'tagline', 'bio', 'unread_notifications')}),
        ('Professional Information', {'fields': ('job_title', 'company_name', 'education', 'location')}),
        ('Social Media Links', {'fields': ('website', 'github', 'linkedin', 'twitter')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'image', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username', 'full_name',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
