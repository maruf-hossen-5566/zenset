from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog_app.models import Blog
from notification_app.models import Notification
import random

User = get_user_model()


class Command(BaseCommand):
    """
    Generate random test notifications between users.
    Creates notifications of different types (like, comment, reply, follow)
    with random users as sender and receiver.
    Default count is 10 notifications.
    """

    help = "Generate random notifications for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=10, help="Number of notifications to generate"
        )

    def handle(self, *args, **options):
        count = options["count"]

        # Get all users and posts
        users = list(User.objects.all())
        posts = list(Blog.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("No users found in the database"))
            return

        if not posts:
            self.stdout.write(self.style.ERROR("No posts found in the database"))
            return

        notification_types = ["like", "comment", "reply", "follow", "others"]
        notifications_created = 0

        for _ in range(count):
            # Randomly select users and post
            user = random.choice(users)
            from_user = random.choice([u for u in users if u != user])  # Exclude self
            post = (
                random.choice(posts) if random.random() > 0.2 else None
            )  # 20% chance of no post
            notification_type = random.choice(notification_types)

            # For follow notifications, post should be None
            if notification_type == "follow":
                post = None

            try:
                Notification.objects.create(
                    user=user,
                    from_user=from_user,
                    type=notification_type,
                    post=post,
                    read=random.choice([True, False]),  # Random read status
                )
                notifications_created += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creating notification: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {notifications_created} notifications"
            )
        )
