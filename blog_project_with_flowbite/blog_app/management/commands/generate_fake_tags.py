import time
from django.core.management.base import BaseCommand
from blog_app.models import Tag
from faker import Faker
from django.utils.text import slugify


class Command(BaseCommand):
    """
    Generate fake tags with random names and descriptions.
    Each tag gets a unique name, slug and description.
    """

    help = "Generates fake tags"

    def add_arguments(self, parser):
        parser.add_argument(
            "count", type=int, help="Indicates the number of tags to be created"
        )

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        fake = Faker()

        start_time = time.time()

        self.stdout.write(self.style.SUCCESS(f"Generating {count} tags..."))

        names = set()
        slugs = set()
        tags = []

        for i in range(count):
            while True:
                name = fake.word().capitalize()
                slug = slugify(name)
                if name not in names and slug not in slugs:
                    names.add(name)
                    slugs.add(slug)
                    long_description = fake.paragraph(
                        nb_sentences=5, variable_nb_sentences=True
                    )
                    tags.append(Tag(name=name, description=long_description, slug=slug))
                    break

            # Calculate and display progress percentage
            progress = (i + 1) / count
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = "=" * filled_length + "-" * (bar_length - filled_length)
            percentage = progress * 100
            self.stdout.write(f"\r[{bar}] {percentage:.1f}% ({i+1}/{count})", ending="")
            self.stdout.flush()

        self.stdout.write("\n")  # New line after progress bar

        Tag.objects.bulk_create(tags)

        end_time = time.time()
        duration = end_time - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {count} fake tags in {duration:.2f} seconds"
            )
        )
