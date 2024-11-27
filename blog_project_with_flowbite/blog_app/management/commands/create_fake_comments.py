from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog_app.models import Blog
from comment_app.models import Comment
from faker import Faker
import random
from django.db.models import Q
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Creates fake comments for blog posts"

    def add_arguments(self, parser):
        parser.add_argument("count", type=int, help="Number of comments to create")

    def handle(self, *args, **kwargs):
        fake = Faker()
        count = kwargs["count"]
        blogs = list(
            Blog.objects.filter(
                Q(is_published=True)
                # & Q(author__id="233c724d-9ae4-4877-9211-a4c848a24467")
            )
        )
        # blogs = list(Blog.objects.filter(is_published=True))
        User = get_user_model()
        users = list(User.objects.all())

        if not blogs:
            self.stdout.write(
                self.style.ERROR(
                    "No published blogs found. Please create some blogs first."
                )
            )
            return

        if not users:
            self.stdout.write(
                self.style.ERROR("No users found. Please create some users first.")
            )
            return

        for i in range(count):
            blog = random.choice(blogs)
            user = random.choice(users)

            # Convert blog_date to a datetime object without timezone
            blog_date = datetime.combine(blog.created_at, datetime.min.time())
            now = datetime.now()  # Use naive datetime for comparison
            random_date = blog_date + timedelta(
                seconds=random.randint(0, int((now - blog_date).total_seconds()))
            )

            comment = Comment.objects.create(
                blog=blog,
                user=user,
                content=fake.paragraph(nb_sentences=random.randint(1, 5)),
                created_at=random_date,
            )

            # Increment the blog's comment count
            blog.increment_comment()

            # Print progress every 10 comments
            if (i + 1) % 10 == 0 or (i + 1) == count:
                self.stdout.write(f"Created {i + 1}/{count} comments")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {count} fake comments")
        )
