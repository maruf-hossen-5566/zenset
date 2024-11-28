import logging
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from blog_app.models import Blog
from notification_app.models import Notification
from .models import Comment, Reply

logger = logging.getLogger("zenset")


@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, *args, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.blog.author,
            from_user=instance.user,
            post=instance.blog,
            comment=instance,
            type="comment",
        )
        # Clear case related to this post
        try:
            if not settings.DEBUG:
                cache_key = f"blog:post_detail:user_{instance.blog.author.id}:*"
                deleted = cache.delete_pattern(cache_key)
                logger.info(
                    f"Cleared blog detail cache for {instance.blog.slug}. Deleted keys: {deleted}"
                )
        except Exception as e:
            logger.error(f"Error clearing blog detail cache: {e}")


@receiver(post_save, sender=Reply)
def send_reply_notification(sender, instance, created, *args, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.comment.blog.author,
            from_user=instance.user,
            post=instance.comment.blog,
            comment=instance.comment,
            reply=instance,
            type="reply",
        )


# --- Clear cache related to this post ---
@receiver([post_save, post_delete], sender=Comment)
def clear_post_detail_cache(sender, instance, created=None, **kwargs):
    try:
        if not settings.DEBUG:
            cache_key = f"blog:post_detail:*:author_{instance.blog.author.username}:slug_{instance.blog.slug}"
            deleted = cache.delete_pattern(cache_key)
            logger.info(
                f"Cleared blog detail cache for {instance.blog.slug}. Deleted keys: {deleted}"
            )
    except Exception as e:
        logger.error(f"Error clearing blog detail cache: {e}")


@receiver([post_save, post_delete], sender=Reply)
def clear_post_detail_cache(sender, instance, created=None, **kwargs):
    try:
        if settings.DEBUG:
            cache.clear()
            logger.info(f"Cleared blog detail cache for {instance.comment.blog.slug}.")
        else:
            cache_key = f"blog:post_detail:*:author_{instance.comment.blog.author.username}:slug_{instance.comment.blog.slug}"
            deleted = cache.delete_pattern(cache_key)
            logger.info(
                f"Cleared blog detail cache for {instance.comment.blog.slug}. Deleted keys: {deleted}"
            )
    except Exception as e:
        logger.error(f"Error clearing blog detail cache: {e}")
