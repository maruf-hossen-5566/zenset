from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from auth_app.models import CustomUser
from profile_app.models import Follow
from django.contrib.messages import get_messages

User: CustomUser = get_user_model()


class TestProfileViews(TestCase):
    def setUp(self):
        """Create two test users and initialize the test client."""
        self.user1 = User.objects.create_user(
            email="user1@test.com",
            username="user1",
            password="testpass1",
            full_name="User 1",
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com",
            username="user2",
            password="testpass2",
            full_name="User 2",
        )
        self.client: Client = Client()

    # --- profile view
    def test_profile(self):
        """Test that profile page loads successfully for existing user."""
        response = self.client.get(
            reverse("profile:profile", kwargs={"username": self.user1.username})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile_app/profile.html")

    def test_nonexistent_user_profile(self):
        """Test that profile page redirects for non-existent user."""

        response = self.client.get(
            reverse("profile:profile", kwargs={"username": "nonexistentuser"})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:index"))

    # --- follow view
    def test_follow_user(self):
        """Test that a logged-in user can follow another user."""
        self.client.login(email="user1@test.com", password="testpass1")
        response = self.client.get(
            reverse("profile:follow", kwargs={"user_id": f"{self.user2.id}"})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Follow.objects.filter(user=self.user2, follower=self.user1).exists()
        )

    def test_unfollow_user(self):
        """Test that a user can unfollow someone they're following."""
        self.client.login(email="user1@test.com", password="testpass1")
        response = self.client.get(
            reverse("profile:follow", kwargs={"user_id": self.user2.id})
        )
        self.assertTrue(Follow.objects.filter(user=self.user2, follower=self.user1))

        response2 = self.client.get(
            reverse("profile:follow", kwargs={"user_id": self.user2.id})
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user2, follower=self.user1).exists()
        )

    def test_follow_yourself(self):
        """Test that users cannot follow themselves."""
        self.client.login(email="user1@test.com", password="testpass1")
        response = self.client.get(
            reverse("profile:follow", kwargs={"user_id": f"{self.user1.id}"})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Follow.objects.filter(user=self.user1, follower=self.user1).exists()
        )

    def test_follow_requires_login(self):
        """Test that following requires user authentication."""
        referer = reverse(
            "profile:profile", kwargs={"username": f"{self.user2.username}"}
        )
        index_url = reverse("blog:index")

        response = self.client.get(
            reverse("profile:follow", kwargs={"user_id": self.user2.id}),
            HTTP_REFERER=f"{referer}",
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            response.url,
            [referer, index_url],
            msg=f"Expected redirect to either '{referer}' or '{index_url}', but got '{response.url}'",
        )
