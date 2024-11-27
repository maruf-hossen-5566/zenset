from django.test import Client, TestCase
from django.urls import reverse
from auth_app.models import CustomUser
from blog_app.models import Blog
from django.contrib.auth import get_user_model
from django.utils import timezone
from comment_app.models import Comment, Reply
from utils.herlpers import pro_print

User = get_user_model()


class TestCommentViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@example.com",
            password="testpassword1",
            full_name="Test User 1",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            password="testpassword2",
            full_name="Test User 2",
        )
        self.blog_data = {
            "title": "Test Blog",
            "content": "This is a test blog post.",
            "author": self.user1,
            "created_at": timezone.now(),
        }
        self.blog = Blog.objects.create(**self.blog_data)
        self.comment_data = {
            "blog": self.blog,
            "user": self.user2,
            "content": "This is a test comment.",
        }

    def test_comment_creation(self):
        """
        Test that a comment can be created
        Login required
        """

        # Login
        self.client.login(email="testuser2@example.com", password="testpassword2")

        # Add comment
        response = self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": self.comment_data["content"]},
        )

        # Test comment exists in database
        comment = Comment.objects.filter(
            blog=self.blog,
            user=self.user2,
            content=self.comment_data["content"],
        ).first()
        self.assertIsNotNone(comment, "Comment was not created")

        self.assertRedirects(
            response,
            reverse(
                "blog:post_detail",
                kwargs={"username": self.user1.username, "slug": self.blog.slug},
            )
            + f"#comment-{comment.id}",  # Add the comment section anchor
            fetch_redirect_response=True,
        )

    def test_unauthenticated_comment_creation(self):
        """
        Test that a comment cannot be created if the user is not authenticated
        """

        # Create comment
        response = self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": self.comment_data["content"]},
        )

        self.assertRedirects(response, reverse("blog:index"))
        self.assertFalse(Comment.objects.filter(**self.comment_data).exists())

    def test_comment_deletion(self):
        """
        Test that a comment can be deleted
        Login required
        """

        # Login
        self.client.login(email="testuser2@example.com", password="testpassword2")

        # Create comment and test it exists
        self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": self.comment_data["content"]},
        )
        comment = Comment.objects.filter(**self.comment_data).first()
        self.assertIsNotNone(comment, "Comment was not created")

        # Delete comment and test it is deleted
        response = self.client.get(
            reverse("comment:comment_delete", kwargs={"id": comment.id}),
        )
        self.assertFalse(
            Comment.objects.filter(**self.comment_data).exists(),
            "Comment was not deleted",
        )

    def test_unauthenticated_comment_deletion(self):
        """
        Test that a comment cannot be deleted if the user is not authenticated
        """

        # Login
        self.client.login(email="testuser2@example.com", password="testpassword2")

        # Create comment and test it exists
        self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": self.comment_data["content"]},
        )
        comment = Comment.objects.filter(**self.comment_data).first()
        self.assertIsNotNone(comment, "Comment was not created")

        # Logout
        self.client.logout()

        # Delete comment and test it is deleted
        response = self.client.get(
            reverse("comment:comment_delete", kwargs={"id": comment.id}),
        )
        self.assertRedirects(response, reverse("blog:index"))
        self.assertTrue(
            Comment.objects.filter(**self.comment_data).exists(),
            "Comment was deleted",
        )

    def test_comment_edit(self):
        """
        Test that a comment can be edited
        Login required
        """

        # Login
        self.client.login(email="testuser2@example.com", password="testpassword2")

        # Create comment and test it exists
        self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": self.comment_data["content"]},
        )
        comment = Comment.objects.filter(**self.comment_data).first()
        self.assertIsNotNone(comment, "Comment was not created")

        # Edit comment and test it is edited
        response = self.client.post(
            reverse("comment:comment_edit", kwargs={"id": comment.id}),
            data={"new_comment": "This is new comment"},
        )
        self.assertRedirects(
            response,
            reverse(
                "blog:post_detail",
                kwargs={
                    "username": self.blog.author.username,
                    "slug": self.blog.slug,
                },
            )
            + f"#comment-{comment.id}",
            msg_prefix="Not redirected to post detail page",
        )
        self.assertTrue(
            Comment.objects.filter(
                id=comment.id,
                content="This is new comment",
            ).exists()
        )

    def test_reply_creation(self):
        """
        Test that a reply can be created for a comment
        Login required
        """

        # Login
        self.client.login(email="testuser1@example.com", password="testpassword1")

        # check blog is created
        self.assertTrue(
            Blog.objects.filter(id=self.blog.id).exists(),
            "Blog was not created",
        )

        # create comment
        response = self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": "This is comment"},
        )

        # Check that is comment created and redirected to post detail page
        comment = Comment.objects.filter(
            blog=self.blog,
            user=self.user1,
            content="This is comment",
        ).first()

        self.assertIsNotNone(comment, "Comment was not created")
        self.assertRedirects(
            response,
            reverse(
                "blog:post_detail",
                kwargs={"username": self.blog.author.username, "slug": self.blog.slug},
            )
            + f"#comment-{comment.id}",
        )

        # Create reply and checks
        reply_content = {
            "user": self.user1,
            "comment": comment,
            "content": f"This is reply for comment {comment.content}",
        }

        response2 = self.client.post(
            reverse("comment:reply", kwargs={"id": comment.id}),
            data={"reply_content": f"This is reply for comment {comment.content}"},
        )

        reply: Reply = Reply.objects.filter(**reply_content).first()
        self.assertIsNotNone(reply, "Reply was not created")
        self.assertEqual(reply.comment, comment, "Reply comment is not correct")
        self.assertEqual(reply.user, self.user1, "Reply user is not correct")
        self.assertEqual(
            reply.content,
            reply_content["content"],
            "Reply content is not correct",
        )

    def test_reply_edit(self):
        """
        Test that a reply can be edited
        Login required
        """

        # Login
        self.client.login(email="testuser1@example.com", password="testpassword1")

        # check blog is created
        self.assertTrue(
            Blog.objects.filter(id=self.blog.id).exists(),
            "Blog was not created",
        )

        # create comment
        response = self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": "This is comment"},
        )

        # Check that is comment created and redirected to post detail page
        comment = Comment.objects.filter(
            blog=self.blog,
            user=self.user1,
            content="This is comment",
        ).first()

        self.assertIsNotNone(comment, "Comment was not created")
        self.assertRedirects(
            response,
            reverse(
                "blog:post_detail",
                kwargs={"username": self.blog.author.username, "slug": self.blog.slug},
            )
            + f"#comment-{comment.id}",
        )

        # Create reply and checks
        reply_content = {
            "user": self.user1,
            "comment": comment,
            "content": f"This is reply for comment {comment.content}",
        }

        response2 = self.client.post(
            reverse("comment:reply", kwargs={"id": comment.id}),
            data={"reply_content": f"This is reply for comment {comment.content}"},
        )

        reply: Reply = Reply.objects.filter(**reply_content).first()
        self.assertIsNotNone(reply, "Reply was not created")
        self.assertEqual(reply.comment, comment, "Reply comment is not correct")
        self.assertEqual(reply.user, self.user1, "Reply user is not correct")
        self.assertEqual(
            reply.content,
            reply_content["content"],
            "Reply content is not correct",
        )

        # Edit reply and checks
        response3 = self.client.post(
            reverse("comment:reply_edit", kwargs={"id": reply.id}),
            data={"new_reply": "This is new reply"},
        )
        self.assertTrue(
            Reply.objects.filter(id=reply.id, content="This is new reply").exists(),
            "Reply was not edited",
        )
        self.assertRedirects(
            response3,
            reverse(
                "blog:post_detail",
                kwargs={"username": self.blog.author.username, "slug": self.blog.slug},
            )
            + f"#comment-{comment.id}",
        )

    def test_reply_deletion(self):
        """
        Test that a reply can be deleted
        Login required
        """

        # Login
        self.client.login(email="testuser1@example.com", password="testpassword1")

        # check blog is created
        self.assertTrue(
            Blog.objects.filter(id=self.blog.id).exists(),
            "Blog was not created",
        )

        # create comment
        response = self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": "This is comment"},
        )

        # Check that is comment created and redirected to post detail page
        comment = Comment.objects.filter(
            blog=self.blog,
            user=self.user1,
            content="This is comment",
        ).first()

        self.assertIsNotNone(comment, "Comment was not created")
        self.assertRedirects(
            response,
            reverse(
                "blog:post_detail",
                kwargs={"username": self.blog.author.username, "slug": self.blog.slug},
            )
            + f"#comment-{comment.id}",
        )

        # Create reply and checks
        reply_content = {
            "user": self.user1,
            "comment": comment,
            "content": f"This is reply for comment {comment.content}",
        }

        response2 = self.client.post(
            reverse("comment:reply", kwargs={"id": comment.id}),
            data={"reply_content": f"This is reply for comment {comment.content}"},
        )

        reply: Reply = Reply.objects.filter(**reply_content).first()
        self.assertIsNotNone(reply, "Reply was not created")

        # Delete reply and checks
        self.client.get(
            reverse("comment:reply_delete", kwargs={"id": reply.id}),
        )
        self.assertFalse(
            Reply.objects.filter(**reply_content).exists(),
            "Reply was not deleted",
        )

    def test_unauthorized_reply_deletion(self):
        """
        Test that a reply cannot be deleted by an unauthorized user
        """

        # Login
        self.client.login(email="testuser1@example.com", password="testpassword1")

        # check blog is created
        self.assertTrue(
            Blog.objects.filter(id=self.blog.id).exists(),
            "Blog was not created",
        )

        # create comment
        response = self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": "This is comment"},
        )

        # Check that is comment created and redirected to post detail page
        comment = Comment.objects.filter(
            blog=self.blog,
            user=self.user1,
            content="This is comment",
        ).first()

        self.assertIsNotNone(comment, "Comment was not created")
        self.assertRedirects(
            response,
            reverse(
                "blog:post_detail",
                kwargs={"username": self.blog.author.username, "slug": self.blog.slug},
            )
            + f"#comment-{comment.id}",
        )

        # Create reply and checks
        reply_content = {
            "user": self.user1,
            "comment": comment,
            "content": f"This is reply for comment {comment.content}",
        }

        response2 = self.client.post(
            reverse("comment:reply", kwargs={"id": comment.id}),
            data={"reply_content": f"This is reply for comment {comment.content}"},
        )

        reply: Reply = Reply.objects.filter(**reply_content).first()
        self.assertIsNotNone(reply, "Reply was not created")

        # Logout
        self.client.logout()

        # Login user2
        self.client.login(email="testuser2@example.com", password="testpassword2")

        # Delete reply and checks
        response3 = self.client.get(
            reverse("comment:reply_delete", kwargs={"id": reply.id}),
        )
        self.assertRedirects(response3, reverse("blog:index"))
        self.assertTrue(
            Reply.objects.filter(**reply_content).exists(),
            "Reply was deleted",
        )

    def test_cascade_reply_deletion(self):
        """
        Test that a reply and all replies to it are deleted when a comment is deleted
        """

        self.client.login(email="testuser1@example.com", password="testpassword1")

        # Create comment and checks
        response = self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": "This is comment"},
        )

        comment = Comment.objects.filter(
            blog=self.blog,
            user=self.user1,
            content="This is comment",
        ).first()
        self.assertIsNotNone(comment, "Comment was not created")

        # Create reply and checks
        reply_content = {
            "user": self.user1,
            "comment": comment,
            "content": f"This is reply for comment {comment.content}",
        }
        response2 = self.client.post(
            reverse("comment:reply", kwargs={"id": comment.id}),
            data={"reply_content": f"This is reply for comment {comment.content}"},
        )

        reply: Reply = Reply.objects.filter(**reply_content).first()
        self.assertIsNotNone(reply, "Reply was not created")

        # Delete comment and checks
        self.client.get(
            reverse("comment:comment_delete", kwargs={"id": comment.id}),
        )
        self.assertFalse(
            Reply.objects.filter(**reply_content).exists(),
            "Reply was not deleted",
        )

    def test_unauthorized_comment_edit(self):
        """
        Test that a comment cannot be edited by an unauthorized user
        """
        # Login as user2 and create comment
        self.client.login(email="testuser2@example.com", password="testpassword2")
        self.client.post(
            reverse("comment:comment_post", kwargs={"id": self.blog.id}),
            data={"comment": self.comment_data["content"]},
        )
        comment = Comment.objects.filter(**self.comment_data).first()
        self.assertIsNotNone(comment, "Comment was not created")

        # Login as user1 (unauthorized user)
        self.client.logout()
        self.client.login(email="testuser1@example.com", password="testpassword1")

        # Try to edit comment
        response = self.client.post(
            reverse("comment:comment_edit", kwargs={"id": comment.id}),
            data={"new_comment": "This is edited comment"},
        )

        # Verify comment was not edited
        self.assertRedirects(response, reverse("blog:index"))
        self.assertTrue(
            Comment.objects.filter(
                id=comment.id, content=self.comment_data["content"]
            ).exists(),
            "Comment was edited by unauthorized user",
        )
