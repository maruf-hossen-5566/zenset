from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "full_name": "Test User",
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(
            user.username, self.user_data["username"], "Username is incorrect"
        )
        self.assertEqual(user.email, self.user_data["email"], "Email is incorrect")
        self.assertTrue(
            user.check_password(self.user_data["password"]), "Password is incorrect"
        )

    def test_create_superuser(self):
        user = User.objects.create_superuser(**self.user_data)
        self.assertTrue(user.is_superuser, "User is not a superuser")
        self.assertTrue(user.is_staff, "User is not a staff")

    def test_user_str_representation(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(
            str(user),
            self.user_data["email"],
            "User string representation is incorrect",
        )
