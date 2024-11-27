from typing import Any
from uuid import UUID
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from auth_app.models import CustomUser
from blog_app.models import Blog
from comment_app.models import Comment


User: CustomUser = get_user_model()


class TestCommentModel(TestCase):
    def setUp(self):
        self.user1: CustomUser = User.objects.create_user(
            email="user1@test.com",
            username="user1",
            password="testpass1",
            full_name="Test User 1",
        )
        self.user2: CustomUser = User.objects.create_user(
            email="user2@test.com",
            username="user2",
            password="testpass2",
            full_name="Test User 2",
        )
        self.blog_data: dict[str, Any] = {
            "title": "Test Blog",
            "content": "Test Content",
            "author": self.user1,
            "created_at": timezone.now(),
        }
        self.blog: Blog = Blog.objects.create(**self.blog_data)
        self.comment_data: dict[str, Any] = {
            "content": "Test Comment",
            "user": self.user2,
        }

    def test_comment_creation(self):
        """Test that a comment can be created"""

        comment: Comment = Comment.objects.create(**self.comment_data, blog=self.blog)

        self.assertIsNotNone(comment, "Comment was not created")
        self.assertEqual(
            comment.content,
            self.comment_data["content"],
            "Comment content is incorrect",
        )
        self.assertEqual(
            comment.user,
            self.comment_data["user"],
            "Comment user is incorrect",
        )
        self.assertEqual(
            comment.blog,
            self.blog,
            "Comment blog is incorrect",
        )

    def test_comment_deletion(self):
        """Test that a comment can be deleted"""

        comment: Comment = Comment.objects.create(**self.comment_data, blog=self.blog)
        self.assertIsNotNone(comment, "Comment was not created")

        # Delete the comment
        comment.delete()
        self.assertFalse(
            Comment.objects.filter(**self.comment_data, blog=self.blog).exists()
        )

    def test_cascade_deletion(self):
        """Test that a comment is deleted when the blog is deleted"""

        comment: Comment = Comment.objects.create(**self.comment_data, blog=self.blog)
        comment_id: UUID = comment.id
        self.assertIsNotNone(comment, "Comment was not created")

        # Delete the blog
        self.blog.delete()

        # Test if blog and comment exists
        self.assertFalse(
            Blog.objects.filter(**self.blog_data).exists(), "Blog was not deleted"
        )
        self.assertFalse(
            Comment.objects.filter(id=comment_id).exists(),
            "The comment was not deleted",
        )
