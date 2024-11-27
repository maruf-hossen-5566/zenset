from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
import logging

User = get_user_model()
logger = logging.getLogger("zenset")


@receiver([post_save, post_delete], sender=User)
def invalidate_user_related_cache(sender, instance, *args, **kwargs):
    """
    Clear all user-related cache when user data changes.
    Invalidates cache for user's pages, homepage, following, trending and latest pages.
    """
    try:
        if not settings.DEBUG:
            patterns = [
                f"blog:*:user_{instance.id}:*",  # All user's cached pages
                "blog:index:*",  # Homepage caches
                "blog:following:*",  # Following page caches
                "blog:trending:*",  # Trending page caches
                "blog:latest:*",  # Latest page caches
            ]

            for pattern in patterns:
                deleted = cache.delete_pattern(pattern, itersize=100_000)
                logger.info(
                    f"Cleared user cache pattern {pattern}. Deleted keys: {deleted}"
                )
        else:
            # Clear cache
            cache.clear()
            logger.info(
                f"User {instance.username} data changed. Clearing user related cache."
            )
    except Exception as e:
        logger.error(f"Error clearing user related cache: {e}")
