from django.test import TestCase, Client
from django.contrib.messages import get_messages
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("auth:register")
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "full_name": "Test User",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.invalid_user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "full_name": "Test User",
        }

    def test_register_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "auth_app/register.html", "Template is incorrect"
        )
        # Check if template has 6 input fields
        self.assertContains(response, "<input", 6)
        # Check if template has 2 password input fields
        self.assertContains(response, '<input type="password"', 2)

    def test_register_view_post(self):
        response = self.client.post(self.url, data=self.user_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("blog:index"), msg_prefix="Redirect is incorrect"
        )
        user = User.objects.get(
            username=self.user_data["username"],
            email=self.user_data["email"],
            full_name=self.user_data["full_name"],
        )
        self.assertIsNotNone(user, "User was not created")
        self.assertTrue(
            user.check_password(self.user_data["password1"]), "Password is incorrect"
        )

    def test_register_view_post_invalid_data(self):
        response = self.client.post(self.url, data=self.invalid_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth_app/register.html")

        # Check if error messages are in response
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0, "No error messages found")
        self.assertEqual(
            messages[0].message, "This field is required.", "Error message is incorrect"
        )

    def test_register_view_post_password_mismatch(self):
        response = self.client.post(
            self.url,
            data={
                **self.user_data,
                "password1": "testpassword1",
                "password2": "testpassword2",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth_app/register.html")

        # Check if error messages are in response
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0, "No error messages found")
        self.assertEqual(
            messages[0].message,
            "The two password fields didn’t match.",
            "Error message is incorrect",
        )


class LoginViewTest(TestCase):
    def setUp(self):
        self.url = reverse("auth:login")
        self.logout_url = reverse("auth:logout")
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            full_name="Test User",
            password="testpassword",
        )
        self.user_data = {
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        self.invalid_user_data = {
            "email": "testuser@example.com",
            "password": "testpassword1",
        }

    def test_login_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth_app/login.html")

    def test_login_view_post(self):
        response = self.client.post(self.url, data=self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("blog:index"), msg_prefix="Redirect is incorrect"
        )

    def test_login_view_post_invalid_data(self):
        response = self.client.post(self.url, data=self.invalid_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth_app/login.html")

        # Check if error messages are in response
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0, "No error messages found")
        self.assertEqual(
            messages[0].message,
            "Invalid credentials!",
            "Error message is incorrect",
        )

    def test_logout_view(self):
        self.client.login(**self.user_data)
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:index"))


class ChangePassViewTest(TestCase):
    def setUp(self):
        self.url = reverse("auth:change_pass")
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            full_name="Test User",
            password="testpassword",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            full_name="Test User 2",
            password="testpassword2",
        )
        self.user_data = {
            "email": "testuser@example.com",
            "password": "testpassword",
        }

    def test_change_pass_view_get(self):
        self.client.login(**self.user_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth_app/change_pass.html")

    def test_change_pass_view_post(self):
        self.client.login(**self.user_data)
        new_password = "newpassword1234"
        response = self.client.post(
            self.url,
            data={
                "old_pass": self.user_data["password"],
                "new_pass": new_password,
                "new_pass_2": new_password,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("auth:login"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0, "No success messages found")
        self.assertEqual(
            messages[0].message,
            "Password changed successfully. Please login with your new password.",
            "Success message is incorrect",
        )
        self.assertTrue(
            User.objects.get(username=self.user.username).check_password(new_password)
        )

    def test_change_pass_view_post_invalid_data(self):
        self.client.login(**self.user_data)
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:index"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0, "No error messages found")
        self.assertEqual(
            messages[0].message,
            "Fill the fields properly.",
            "Error message is incorrect",
        )

    def test_change_pass_view_post_old_password_incorrect(self):
        self.client.login(**self.user_data)
        response = self.client.post(
            self.url,
            data={
                "old_pass": "testpassword1",
                "new_pass": "newpassword1234",
                "new_pass_2": "newpassword1234",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:index"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0, "No error messages found")
        self.assertEqual(
            messages[0].message,
            "Current password is incorrect!",
            "Error message is incorrect",
        )
