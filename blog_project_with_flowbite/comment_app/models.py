from django.db import models
from blog_app.models import Blog
from django.contrib.auth import get_user_model
import uuid
from django.db.models import Case, When, F

User = get_user_model()


# Create your models here.
class Comment(models.Model):
    """
    Store comments on blog posts.
    Tracks reply count and maintains timestamps.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    reply_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by @{self.user.username} on {self.blog.title[:50]}... - {self.content[:50]}..."

    def increment_reply_count(self):
        """Safely increment the comment's reply count."""
        self.reply_count = models.F("reply_count") + 1
        self.save(update_fields=["reply_count"])

    def decrement_reply_count(self):
        """Safely decrement the comment's reply count, never going below 0."""
        self.reply_count = Case(
            When(reply_count__gt=0, then=F("reply_count") - 1),
            default=F("reply_count"),
        )
        self.save(update_fields=["reply_count"])


class Reply(models.Model):
    """
    Store replies to comments.
    Supports nested replies through parent_reply field.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="replies"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    parent_reply = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Replied by @{self.user.username} on {self.comment.content[:50]}... - {self.content[:50]}..."
            if self.parent_reply is None
            else f"Replied by @{self.user.username} to @{self.parent_reply.user.username} - {self.content[:50]}..."
        )
