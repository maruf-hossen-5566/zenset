import uuid
from django.db import models
from django.contrib.auth import get_user_model
from blog_app.models import Blog
from comment_app.models import Comment, Reply

User = get_user_model()

# Create your models here.
TYPES = (
    ("like", "Like"),
    ("comment", "Comment"),
    ("reply", "Reply"),
    ("follow", "Follow"),
    ("others", "Others"),
)


class Notification(models.Model):
    """
    Store user notifications for various activities.
    Supports different notification types and tracks read status.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # User who'll receives the notification
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications", null=True
    )
    # User who triggered the notification (who liked, commented, followed, etc.)
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications_sent", null=True
    )
    post = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    type = models.CharField(max_length=100, choices=TYPES, default="like")
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    reply = models.ForeignKey(
        Reply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    # session_key = models.CharField(max_length=100, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.from_user.username} {self.type}d {self.post.title if self.post else ''}"

    def mark_as_read(self):
        """Mark the notification as read if it hasn't been read yet."""
        if not self.read:
            self.read = True
            self.save()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]
