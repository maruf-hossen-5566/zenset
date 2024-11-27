from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from auth_app.models import CustomUser
from blog_app.models import Blog, Tag, TagFollow
from utils.herlpers import pro_print

User: CustomUser = get_user_model()


class TestBlogCreationAndDeletion(TestCase):
    def setUp(self) -> None:
        self.client = Client()
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

    # Blog creation related tests
    def test_unauthenticated_blog_create(self):
        """Test that unauthenticated users cannot access the blog creation page."""

        response = self.client.get(reverse("blog:create_post"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:index"))

    def test_authenticated_blog_create(self):
        """Test that authenticated users can access the blog creation page."""

        # Login
        self.client.login(email=self.user1.email, password="testpass1")

        response = self.client.get(reverse("blog:create_post"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog_app/create_post.html")

    def test_authenticated_blog_create_success(self):
        """Test that authenticated users can create blog post."""

        # Login
        self.client.login(email=self.user1.email, password="testpass1")

        response = self.client.post(
            reverse("blog:create_post"),
            data={
                "title": "This is blog title",
                "content": "This is blog content",
            },
        )

        blog: Blog = Blog.objects.first()

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            reverse(
                "blog:post_detail",
                kwargs={"username": f"{blog.author.username}", "slug": f"{blog.slug}"},
            ),
        )

    def test_authenticated_draft_blog_create_success(self):
        """Test that authenticated users can create draft post."""

        self.client.login(email=self.user1.email, password="testpass1")

        # blog data
        title = "This is draft blog title 2"
        content = "This is draft blog content"

        response = self.client.post(
            reverse("blog:create_draft_post"),
            data={
                "title": title,
                "content": content,
            },
        )
        self.assertEqual(response.status_code, 302)

        blog: Blog = Blog.objects.filter(
            title=title,
            content=content,
            author=self.user1,
            is_published=False,
        ).first()
        self.assertIsNotNone(blog, "Draft blog post was not created")
        self.assertFalse(blog.is_published)

    # Blog deletion related tests
    def test_unauthenticated_blog_delete(self):
        """Test that authorized user cannot delete blog."""

        # blog data
        title = "This is blog title"
        content = "This is blog content"

        # Creating blog as user1
        response = self.client.post(
            reverse("blog:create_post"),
            data={
                "title": title,
                "content": content,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:index"))
        blog: Blog = Blog.objects.filter(
            title=title,
            content=content,
            author=self.user1,
            is_published=True,
        ).first()
        self.assertIsNone(blog, "Blog was not created")

    def test_unauthorized_blog_delete(self):
        """Test that unauthorized user cannot delete blog."""

        # Login as user1
        self.client.login(email=self.user1.email, password="testpass1")

        # blog data
        title = "This is blog title"
        content = "This is blog content"

        # Creating blog as user1
        response = self.client.post(
            reverse("blog:create_post"),
            data={
                "title": title,
                "content": content,
            },
        )

        self.assertEqual(response.status_code, 302)
        blog: Blog = Blog.objects.filter(
            title=title,
            content=content,
            author=self.user1,
            is_published=True,
        ).first()
        self.assertIsNotNone(blog, "Blog was not created")
        # Now logout the user1
        self.client.logout()

        # Now, log in as user2 and try to delete the blog created by user1
        self.client.login(email=self.user2.email, password="testpass2")
        response = self.client.get(reverse("blog:delete_post", kwargs={"id": blog.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:index"))

    def test_authorized_blog_delete(self):
        """Test that authorized user can delete blog."""

        self.client.login(email=self.user1.email, password="testpass1")

        # blog data
        title = "This is blog title"
        content = "This is blog content"

        response = self.client.post(
            reverse("blog:create_post"),
            data={
                "title": title,
                "content": content,
            },
        )

        self.assertEqual(response.status_code, 302)
        blog: Blog = Blog.objects.filter(
            title=title,
            content=content,
            author=self.user1,
            is_published=True,
        ).first()
        self.assertIsNotNone(blog, "Blog was not created.")

        # Now, try to delete the blog
        response = self.client.get(
            reverse("blog:delete_post", kwargs={"id": f"{blog.id}"})
        )
        self.assertRedirects(response, reverse("blog:index"))
        delete_blog: Blog = Blog.objects.filter(
            title=title,
            content=content,
            author=self.user1,
            is_published=True,
        ).first()
        self.assertIsNone(delete_blog, "Blog was not deleted.")
