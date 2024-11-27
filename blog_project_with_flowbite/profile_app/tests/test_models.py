from django.test import TestCase
from django.contrib.auth import get_user_model
from profile_app.models import Follow

User = get_user_model()


class ProfileModelTests(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(
            email="user1@test.com",
            username="testuser1",
            password="testpass1234",
            full_name="Test User 1",
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com",
            username="testuser2",
            password="testpass1234",
            full_name="Test User 2",
        )

    def test_follow_creation(self):
        """Test creating a follow relationship"""
        follow = Follow.objects.create(user=self.user1, follower=self.user2)
        self.assertEqual(follow.user, self.user1)
        self.assertEqual(follow.follower, self.user2)

    def test_follow_str_method(self):
        """Test the string representation of the Follow model"""
        follow = Follow.objects.create(user=self.user1, follower=self.user2)
        expected_str: str = f"{self.user2.full_name} - follows - {self.user1.full_name}"
        self.assertEqual(str(follow), expected_str, "Not equal to each other")

    def test_follow_related_names(self):
        """Test the relations for followers and following"""
        follow = Follow.objects.create(user=self.user1, follower=self.user2)

        self.assertTrue(
            self.user1.followers.filter(follower=self.user2).exists(),
            msg="user1 has no follower named user2",
        )
        self.assertTrue(
            self.user2.following.filter(user=self.user1).exists(),
            msg="user2 is not following any user named user1",
        )
