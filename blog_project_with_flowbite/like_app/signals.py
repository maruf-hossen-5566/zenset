from django.db.models.signals import post_save
from django.dispatch import receiver
from notification_app.models import Notification
from .models import Like


@receiver(post_save, sender=Like)
def send_like_notification(sender, instance, created, *args, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.blog.author,
            from_user=instance.user,
            post=instance.blog,
            type="like",
        )
