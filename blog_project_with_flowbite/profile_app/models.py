import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# Create your models here.
class Follow(models.Model):
    """
    Track follower relationships between users.
    Stores both the follower and the followed user.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name=_("User to follow"),
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name=_("Follower"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower.full_name} - follows - {self.user.full_name}"

    class Meta:
        unique_together = ("user", "follower")
