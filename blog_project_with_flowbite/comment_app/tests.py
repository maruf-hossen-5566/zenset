from django.test import TestCase
from django.contrib.auth import get_user_model
from blog_app.models import Blog
from comment_app.models import Comment, Reply
from django.urls import reverse

User = get_user_model()

class CommentAndReplyTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            full_name='Test User'
        )
        
        # Create a test blog post
        self.blog = Blog.objects.create(
            title='Test Blog',
            content='This is a test blog post.',
            slug='test-blog',
            author=self.user
        )
        
        # Create a test comment
        self.comment = Comment.objects.create(
            blog=self.blog,
            user=self.user,
            content='This is a test comment.'
        )

    def test_comment_creation(self):
        """Test that a comment can be created"""
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.comment.content, 'This is a test comment.')
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.blog, self.blog)

    def test_reply_creation(self):
        """Test that a reply can be created"""
        reply = Reply.objects.create(
            comment=self.comment,
            user=self.user,
            content='This is a test reply.'
        )
        self.assertEqual(Reply.objects.count(), 1)
        self.assertEqual(reply.content, 'This is a test reply.')
        self.assertEqual(reply.user, self.user)
        self.assertEqual(reply.comment, self.comment)

    def test_nested_reply_creation(self):
        """Test that a nested reply can be created"""
        parent_reply = Reply.objects.create(
            comment=self.comment,
            user=self.user,
            content='This is a parent reply.'
        )
        child_reply = Reply.objects.create(
            comment=self.comment,
            user=self.user,
            parent_reply=parent_reply,
            content='This is a child reply.'
        )
        self.assertEqual(Reply.objects.count(), 2)
        self.assertEqual(child_reply.parent_reply, parent_reply)

    def test_comment_str_method(self):
        """Test the string representation of a Comment"""
        expected_str = f"Comment by @{self.user.username} on {self.blog.title[:50]}... - {self.comment.content[:50]}..."
        self.assertEqual(str(self.comment), expected_str)

    def test_reply_str_method(self):
        """Test the string representation of a Reply"""
        reply = Reply.objects.create(
            comment=self.comment,
            user=self.user,
            content='This is a test reply.'
        )
        expected_str = f"Replied by @{self.user.username} on {self.comment.content[:50]}... - {reply.content[:50]}..."
        self.assertEqual(str(reply), expected_str)

    def test_comment_post_view(self):
        """Test the comment_post view"""
        self.client.login(email='testuser@example.com', password='testpassword123')
        response = self.client.post(reverse('comment:comment_post', kwargs={'id': self.blog.id}), {
            'comment': 'This is a new comment.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(Comment.objects.count(), 2)
        new_comment = Comment.objects.latest('created_at')
        self.assertEqual(new_comment.content, 'This is a new comment.')

    def test_reply_view(self):
        """Test the reply view"""
        self.client.login(email='testuser@example.com', password='testpassword123')
        response = self.client.post(reverse('comment:reply', kwargs={'id': self.comment.id}), {
            'reply_content': 'This is a new reply.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(Reply.objects.count(), 1)
        new_reply = Reply.objects.first()
        self.assertEqual(new_reply.content, 'This is a new reply.')
