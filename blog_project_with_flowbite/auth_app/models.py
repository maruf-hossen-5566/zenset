from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from cloudinary.models import CloudinaryField


# Create your models here.
class CustomUserManager(UserManager):
    """Custom manager for User model with email as the unique identifier."""

    def _create_user(self, email, username, password, **extra_fields):
        """Create and save a user with the given email, username, and password."""
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a regular user."""
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff") or not extra_fields.get("is_superuser"):
            raise ValueError(
                _("Superuser must have is_staff=True and is_superuser=True.")
            )

        return self._create_user(email, username, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom user model with additional fields for user profile.
    Uses email for authentication instead of username.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = CloudinaryField("profile_pictures", folder="profile_pictures", null=True, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=150, blank=True)
    bio = models.TextField(blank=True)
    tagline = models.TextField(_("tagline"), max_length=200, blank=True)
    unread_notifications = models.IntegerField(default=0)
    # --- Professional Information ---
    job_title = models.CharField(_("job title"), max_length=100, blank=True)
    company_name = models.CharField(_("company name"), max_length=100, blank=True)
    education = models.CharField(_("education"), max_length=100, blank=True)
    location = models.CharField(_("location"), max_length=100, blank=True)
    # --- Social Media Links ---
    website = models.URLField(_("website"), blank=True)
    github = models.URLField(_("github"), blank=True)
    linkedin = models.URLField(_("linkedin"), blank=True)
    twitter = models.URLField(_("twitter"), blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "full_name"]

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email

    def get_followed_authors(self):
        """Get the author followed by the user"""
        return self.following.all()

    def get_followed_tags(self):
        """Get all tags followed by the user"""
        return self.followed_tags.all()

    def follows_tag(self, tag):
        """Check if user follows a specific tag"""
        return self.tag_follows.filter(tag=tag).exists()
