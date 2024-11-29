import time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog_app.models import Blog, Tag
from faker import Faker
from django.utils.text import slugify
import random
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    """
    Generate fake blog posts with random data.
    Each blog gets a unique title, content, author, tags, and realistic timestamps.
    Also generates random like and view counts for each blog.
    """

    help = "Generates fake blogs"

    def add_arguments(self, parser):
        parser.add_argument(
            "count", type=int, help="Indicates the number of blogs to be created"
        )

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        fake = Faker()

        start_time = time.time()

        users = list(User.objects.all())
        tags = list(Tag.objects.all())

        if not users or not tags:
            self.stdout.write(
                self.style.ERROR(
                    "Please ensure you have users and tags in the database"
                )
            )
            return

        self.stdout.write(self.style.SUCCESS(f"Generating {count} blogs..."))

        def generate_paragraph():
            return f"<p>{' '.join(fake.sentences(nb=random.randint(3, 8)))}</p>"

        def generate_content():
            num_paragraphs = random.randint(4, 8)
            paragraphs = [generate_paragraph() for _ in range(num_paragraphs)]
            return "\n\n".join(paragraphs)

        # Generate all dates upfront
        all_dates = []
        now = datetime.now()
        start_date = now - timedelta(days=730)  # 2 years ago

        for _ in range(count):
            random_date = start_date + timedelta(
                days=random.randint(0, 730),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            )
            all_dates.append(random_date)

        # Sort dates to make them more realistic (optional)
        all_dates.sort(reverse=True)

        for i in range(count):

            title = " ".join(fake.sentences(nb=random.randint(1, 3)))
            blog = Blog.objects.create(
                title=title,
                content=generate_content(),
                slug=slugify(title),
                author=random.choice(users),
                created_at=fake.date_between(
                    start_date=datetime(2024, 1, 1), end_date=datetime.today()
                ),
                likes_count=random.randint(9999, 49999),
                views_count=random.randint(99999, 999999),
            )
            blog.tags.set(random.sample(tags, random.randint(2, 5)))

            # Calculate and display progress percentage
            progress = (i + 1) / count
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = "=" * filled_length + "-" * (bar_length - filled_length)
            percentage = progress * 100
            self.stdout.write(f"\r[{bar}] {percentage:.1f}% ({i+1}/{count})", ending="")
            self.stdout.flush()

        self.stdout.write("\n")  # New line after progress bar

        end_time = time.time()
        duration = end_time - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {count} fake blogs in {duration:.2f} seconds"
            )
        )
