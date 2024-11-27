from django.contrib import admin
from .models import Blog, Bookmark, Tag

# Register your models here.


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "author", "is_published", "created_at", "updated_at")
    list_filter = ("is_published", "is_featured", "tags")
    search_fields = ("title", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "blog", "created_at")
    search_fields = ("user_username", "blog__title")
