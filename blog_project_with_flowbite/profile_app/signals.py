import logging
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models import F
from profile_app.models import Follow
from notification_app.models import Notification
from django.core.cache import cache
from django.db import transaction


logger = logging.getLogger("zenset")
User = get_user_model()


@receiver([post_save, post_delete], sender=Follow)
def notify_user_about_new_follower(sender, instance, created=False, **kwargs):
    """
    Create or delete notification when user is followed/unfollowed.
    Updates unread notification count for the followed user.
    """

    try:
        if settings.DEBUG:
            cache.clear()
            logger.info("Cleared notifications cache.")
        else:
            obj_args = {
                "user": instance.user,
                "from_user": instance.follower,
                "type": "follow",
            }
            with transaction.atomic():
                if created:
                    obj = Notification.objects.create(**obj_args)
                    # Update unread notification count
                    obj.user.unread_notifications = F("unread_notifications") + 1
                    obj.user.save()
                else:
                    # Delete notification if unfollow
                    obj = Notification.objects.filter(**obj_args).first()
                    if obj:
                        obj.delete()

    except Exception as e:
        logger.error(f"Error in notification signal: {e}")


@receiver([post_save, post_delete], sender=Follow)
def clear_cache_on_follow(sender, instance, created=False, *args, **kwargs):
    """
    Clear following-related cache when follow relationship changes.
    Clears cache for both follower and followed user.
    """
    try:
        if settings.DEBUG:
            cache.clear()
            logger.info("Cleared following cache.")
        else:
            cache_keys = [
                f"blog:following:user_{instance.follower.id}:*",
                f"blog:following:user_{instance.user.id}:*",
            ]
            for cache_key in cache_keys:
                cache.delete_pattern(cache_key, itersize=100_000)
    except Exception as e:
        logger.error(f"Error clearing following cache: {e}")
