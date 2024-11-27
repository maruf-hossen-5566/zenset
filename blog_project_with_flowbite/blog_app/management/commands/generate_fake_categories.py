import time
from django.core.management.base import BaseCommand
from blog_app.models import Category
from faker import Faker
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Generates fake categories'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Indicates the number of categories to be created')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        fake = Faker()

        start_time = time.time()

        # Pre-generate all data
        category_names = set()
        categories = []

        self.stdout.write(self.style.SUCCESS(f"Generating {count} categories..."))

        for i in range(count):
            while True:
                category_name = f"{fake.word().capitalize()} {fake.word().capitalize()}"
                category_slug = slugify(category_name)
                if category_name not in category_names:
                    category_names.add(category_name)
                    long_description = fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
                    categories.append(Category(name=category_name, slug=category_slug, description=long_description))
                    break
            
            # Calculate and display progress percentage
            progress = (i + 1) / count
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = '=' * filled_length + '-' * (bar_length - filled_length)
            percentage = progress * 100
            self.stdout.write(f"\r[{bar}] {percentage:.1f}% ({i+1}/{count})", ending='')
            self.stdout.flush()

        self.stdout.write("\n")  # New line after progress bar
        Category.objects.bulk_create(categories)

        end_time = time.time()
        duration = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} categories in {duration:.2f} seconds"))
