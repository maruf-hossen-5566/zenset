import uuid
from django.urls import reverse
from django.utils.text import slugify
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import F, When, Case, Value
from django.utils.html import strip_tags
from cloudinary.models import CloudinaryField
import logging
import cloudinary.uploader


User = get_user_model()
logger = logging.getLogger(__name__)


# Create your models here.
class Blog(models.Model):
    """
    Blog post model storing all post-related information.
    Includes content, metadata, and engagement metrics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    content_preview = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True, max_length=999)
    image = CloudinaryField(
        "image",
        folder="blog_images",
        blank=True,
        null=True,
        transformation={
            "quality": "auto",
            "fetch_format": "auto",
        },
    )
    # created_at = models.DateField(auto_now_add=True)
    created_at = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    disable_comments = models.BooleanField(default=False)
    pin_to_profile = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs")
    tags = models.ManyToManyField("Tag", related_name="blogs", blank=True)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title[:35]}..."

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.slug:
            self.slug = self.generate_blog_slug()
        if not self.content_preview and self.content:
            # Create a preview from the main content
            cleaned_content = strip_tags(self.content)
            self.content_preview = cleaned_content[:200]
        super().save(*args, **kwargs)

        if is_new:
            logger.info(
                f"New blog post created: {self.title} by {self.author.username}"
            )
        else:
            logger.info(f"Blog post updated: {self.title} by {self.author.username}")

    def generate_blog_slug(self):
        """Generate a unique slug for the blog post using title and UUID."""
        u_id = uuid.uuid4().hex[:6]
        slug = slugify(self.title)
        return f"{slug}-{u_id}"

    def increment_like(self):
        """Safely increment the post's like count."""
        self.likes_count = F("likes_count") + 1
        self.save(update_fields=["likes_count"])

    def decrement_like(self):
        """Safely decrement the post's like count, never going below 0."""
        self.likes_count = Case(
            When(likes_count__gt=0, then=F("likes_count") - 1),
            default=Value(0),
        )
        self.save(update_fields=["likes_count"])

    def increment_comment(self):
        self.comments_count = F("comments_count") + 1
        self.save(update_fields=["comments_count"])

    def decrement_comment(self):
        self.comments_count = Case(
            When(comments_count__gt=0, then=F("comments_count") - 1),
            default=F("comments_count"),
        )
        self.save(update_fields=["comments_count"])

    def get_absolute_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={
                "username": self.author.username,
                "slug": self.slug,
            },
        )

    def delete(self, *args, **kwargs):
        logger.info(f"Deleting blog post: {self.title} by {self.author.username}")
        # If there's an image, delete it from Cloudinary
        if self.image:
            try:
                logger.info(f"Attempting to delete image for post: {self.title}")
                cloudinary.uploader.destroy(self.image.public_id)
                logger.info(f"Successfully deleted image for post: {self.title}")
            except Exception as e:
                logger.error(
                    f"Error deleting image for post {self.title}: {e}", exc_info=True
                )
        super().delete(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at", "is_featured"]),
            models.Index(fields=["author", "is_published"]),
            models.Index(fields=["slug"]),
        ]


class Tag(models.Model):
    """
    Tag model for categorizing blog posts.
    Includes following functionality for users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    followers = models.ManyToManyField(
        User, through="TagFollow", related_name="followed_tags"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["-created_at"]),
        ]

    def is_followed_by(self, user):
        """Check if a given user follows this tag."""
        if not user.is_authenticated:
            return False
        return self.tag_follows.filter(user=user).exists()

    def follow(self, user):
        """Make a user follow this tag"""
        if not self.is_followed_by(user):
            TagFollow.objects.create(user=user, tag=self)

    def unfollow(self, user):
        """Make a user unfollow this tag"""
        self.tag_follows.filter(user=user).delete()


class TagFollow(models.Model):
    """Track which users follow which tags."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tag_follows")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="tag_follows")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "tag")
        indexes = [
            models.Index(fields=["user", "tag"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} follows {self.tag.name}"


class Bookmark(models.Model):
    """Store user bookmarks for blog posts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)
