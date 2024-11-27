from datetime import timedelta
import uuid
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth import get_user_model
from like_app.models import Like
from notification_app.models import Notification
from profile_app.models import Follow
from utils.herlpers import pro_print
from django.db import transaction
from django.db.models import F
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from user_sessions.models import Session
import logging


User = get_user_model()
logger = logging.getLogger("zenset")


@receiver([post_save, post_delete], sender=Notification)
def clear_notifications_cache(sender, instance, created=False, **kwargs):
    """
    Manage notification counts and cleanup old notifications.
    Updates unread notification count and removes notifications older than 30 days.
    """
    try:
        if created:
            user = instance.user
            with transaction.atomic():
                unread_notification_count = user.notifications.filter(
                    read=False
                ).count()
                user.unread_notifications = unread_notification_count
                user.save()

                threshold_date = timezone.now() - timedelta(days=30)
                deleted_count = user.notifications.filter(
                    created_at__lt=threshold_date
                ).delete()[0]
                logger.info(
                    f"Cleaned up {deleted_count} old notifications for user {user.id}"
                )

        if not settings.DEBUG:
            cache_key = f"notification:user_{instance.user.id}:*"
            deleted = cache.delete_pattern(cache_key)
            logger.info(
                f"Cleared notification cache for user {instance.user.id}. Deleted keys: {deleted}"
            )
        else:
            cache.clear()
            logger.info("Cleared notifications cache.")
    except Exception as e:
        logger.error(f"Error in notification signal: {e}")


@receiver([post_save, post_delete], sender=Like)
def notify_user_about_new_like(sender, instance, created=False, **kwargs):
    """
    Create or delete notification when post is liked/unliked.
    Updates unread notification count for the post author.
    """

    try:
        if not settings.DEBUG:
            obj_args = {
                "from_user": instance.user,
                "user": instance.blog.author,
                "post": instance.blog,
                "type": "like",
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
        else:
            cache.clear()
            logger.info("Cleared notifications cache.")

    except Exception as e:
        logger.error(f"Error in notification signal: {e}")
