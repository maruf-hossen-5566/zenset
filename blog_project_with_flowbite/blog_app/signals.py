from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from blog_app.models import Blog, TagFollow
from profile_app.models import Follow
from django.core.cache import cache
from django.conf import settings
import logging

User = get_user_model()

logger = logging.getLogger("zenset")


@receiver([post_save, post_delete], sender=Blog)
def clear_post_detail_cache(sender, instance, created=None, **kwargs):
    try:
        if settings.DEBUG:
            cache.clear()
            logger.info(f"Cleared blog detail cache for {instance.slug}.")
        else:
            cache_key = f"blog:post_detail:*:author_{instance.author.username}:slug_{instance.slug}"
            deleted = cache.delete_pattern(cache_key)
            logger.info(
                f"Cleared blog detail cache for {instance.slug}. Deleted keys: {deleted}"
            )
    except Exception as e:
        logger.error(f"Error clearing blog detail cache: {e}")


@receiver([post_save, post_delete], sender=Follow)
def update_cache_on_blog_create_or_delete(sender, instance, *args, **kwargs):
    """Clear all blog-related cache when a blog is created or deleted."""
    try:
        if settings.DEBUG:
            cache.clear()
            logger.info(f"Cleared blog cache.")
        else:
            cache_key = "blog:*"
            deleted = cache.delete_pattern(cache_key)
            logger.info(f"Cleared blog cache. Deleted keys: {deleted}")
    except Exception as e:
        logger.error(f"Error clearing blog cache: {e}")


@receiver([post_save, post_delete], sender=TagFollow)
def update_cache_on_tag_follow(sender, instance, *args, **kwargs):
    """Clear user-specific cache when they follow/unfollow a tag."""
    try:
        if settings.DEBUG:
            cache.clear()
            logger.info(f"Cleared user-specific cache.")
        else:
            cache_key = f"blog:*:user_{instance.user.id}*"
            deleted = cache.delete_pattern(cache_key)
            logger.info(f"Cleared user-specific cache. Deleted keys: {deleted}")
    except Exception as e:
        logger.error(f"Error clearing user-specific cache: {e}")
