from django.test import TestCase
from django.contrib.auth import get_user_model
from auth_app.models import CustomUser
from blog_app.models import Blog, Tag, TagFollow
from django.utils import timezone
from django.urls import reverse

from like_app.models import Like


User: CustomUser = get_user_model()


class TestBlogModel(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="username1",
            email="user1@test.com",
            password="testpass1",
            full_name="Test User 1",
        )
        self.user2 = User.objects.create_user(
            username="username2",
            email="user2@test.com",
            password="testpass2",
            full_name="Test User 2",
        )
        self.blog_data = {
            "title": "This is blog title",
            "content": "This is blog content",
            "author": self.user1,
            "created_at": timezone.now(),
        }

    def test_blog_creation(self):
        """Test blog creation with valid data and auto slug generation"""

        blog: Blog = Blog.objects.create(
            title=self.blog_data["title"],
            content=self.blog_data["content"],
            author=self.blog_data["author"],
            created_at=self.blog_data["created_at"],
        )

        self.assertIsNotNone(blog, "Blog was not created")
        self.assertEqual(
            blog.title, self.blog_data["title"], "Blog title doesn't match"
        )
        self.assertTrue(
            blog.slug.startswith("this-is-blog-title-"), "Slug prefix is incorrect"
        )
        self.assertEqual(
            len(blog.slug.split("-")[-1]), 6, "UUID part of slug is incorrect length"
        )
        self.assertEqual(blog.author, self.user1, "Author wasn't set correctly")
        self.assertTrue(blog.is_published, "Blog is not published yet")

    def test_blog_str_representation(self):
        """Test blog string representation"""

        blog: Blog = Blog.objects.create(
            title=self.blog_data["title"],
            content=self.blog_data["content"],
            author=self.blog_data["author"],
            created_at=self.blog_data["created_at"],
        )
        expected_str_rep = f"{self.blog_data["title"]}"
        self.assertEqual(str(blog), str(f"{expected_str_rep[:35]}..."))

    def test_get_absolute_url(self):
        """Test blog detail URL generation"""
        blog: Blog = Blog.objects.create(
            title=self.blog_data["title"],
            content=self.blog_data["content"],
            author=self.blog_data["author"],
            created_at=self.blog_data["created_at"],
        )

        expected_url = f"{reverse("blog:post_detail", kwargs={"username":f"{blog.author.username}", "slug":f"{blog.slug}"})}"
        self.assertEqual(
            blog.get_absolute_url(), expected_url, "Blog's absolute url didn't match"
        )

    def test_cascade_deletion(self):
        """Test blogs are delete when author s deleted"""

        blog: Blog = Blog.objects.create(
            title=self.blog_data["title"],
            content=self.blog_data["content"],
            author=self.blog_data["author"],
            created_at=self.blog_data["created_at"],
        )

        self.assertTrue(
            Blog.objects.filter(id=blog.id).exists(), "Blog was not created"
        )

        # Delete the author
        self.user1.delete()

        # Verify the blog existence ->
        self.assertFalse(
            Blog.objects.filter(id=blog.id).exists(), "Blog was not deleted"
        )

    def test_blog_likes(self):
        """Test adding and removing likes from blog"""

        blog: Blog = Blog.objects.create(
            title=self.blog_data["title"],
            content=self.blog_data["content"],
            author=self.blog_data["author"],
            created_at=self.blog_data["created_at"],
        )
        self.assertIsNotNone(blog, "Blog was not created.")

        # Like the blog and increment the likes_count
        like: Like = Like.objects.create(blog=blog, user=self.user2)
        blog.increment_like()

        # Refresh from database to get updated likes_count <- This is must be added to get updated value after F() expression
        blog.refresh_from_db()

        # Test
        self.assertTrue(
            Like.objects.filter(blog=blog, user=self.user2).exists(),
            "Like was not created",
        )
        self.assertEqual(
            blog.likes_count, int(1), "Blog likes_count was not incremented"
        )

        # Now undo like and decrement the blog likes count
        like.delete()  # Undo like means deleting the like object
        blog.decrement_like()

        # Refresh from database to get updated likes_count <- This is must be added to get updated value after F() expression
        blog.refresh_from_db()

        # Test
        self.assertFalse(
            Like.objects.filter(blog=blog, user=self.user2).exists(),
            "Like was not deleted",
        )
        self.assertEqual(blog.likes_count, 0, "Blog likes_count was not decremented")


class TestTagModel(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="username1",
            email="user1@test.com",
            password="testpass1",
            full_name="Test User 1",
        )
        self.user2 = User.objects.create_user(
            username="username2",
            email="user2@test.com",
            password="testpass2",
            full_name="Test User 2",
        )
        self.tag_data = {
            "name": "Python",
            "description": "Python programming language",
            "slug": "python",
        }

    def test_tag_creation(self):
        """Test tag creation with valid data"""
        tag = Tag.objects.create(**self.tag_data)

        self.assertIsNotNone(tag, "Tag was not created")
        self.assertEqual(tag.name, self.tag_data["name"], "Tag name doesn't match")
        self.assertEqual(tag.slug, self.tag_data["slug"], "Tag slug doesn't match")
        self.assertEqual(
            tag.description,
            self.tag_data["description"],
            "Tag description doesn't match",
        )

    def test_tag_str_representation(self):
        """Test tag string representation"""

        tag: Tag = Tag.objects.create(**self.tag_data)

        self.assertEqual(str(tag), self.tag_data["name"])

    def test_tag_following(self):
        """Test tag follow/unfollow functionality"""

        tag: Tag = Tag.objects.create(**self.tag_data)

        # Test initial state
        self.assertFalse(
            tag.is_followed_by(self.user1), "User shouldn't follow tag initially"
        )

        # Test following
        tag.follow(self.user1)
        self.assertTrue(tag.is_followed_by(self.user1), "User should be following tag")
        self.assertEqual(tag.followers.count(), 1, "Tag should have one follower")

        # Tag unfollowing
        tag.unfollow(self.user1)
        self.assertFalse(
            tag.is_followed_by(self.user1),
            "User shouldn't be following tag after unfollow",
        )
        self.assertEqual(tag.followers.count(), 0, "Tag should have no followers")

    def test_tag_unique_follow(self):
        """Test that a user can't follow a tag twice"""

        tag = Tag.objects.create(**self.tag_data)

        # First follow
        tag.follow(self.user1)
        initial_follow_count = TagFollow.objects.count()

        # Try to follow again
        tag.follow(self.user1)
        self.assertEqual(
            TagFollow.objects.count(),
            initial_follow_count,
            "Duplicate follow should not create new TagFollow",
        )
