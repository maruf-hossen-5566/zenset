from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from django.contrib.auth.hashers import make_password
from django.db import transaction
import time

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates fake users'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Indicates the number of users to be created')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        fake = Faker()

        start_time = time.time()

        # Pre-generate all data
        hashed_password = make_password("/'[p;.,l")
        usernames = set()
        emails = set()
        users = []

        self.stdout.write(self.style.SUCCESS(f"Generating {count} users..."))

        for i in range(count):
            while True:
                username = fake.user_name()
                email = fake.email()
                bio = fake.paragraph(nb_sentences=5)
                if username not in usernames and email not in emails:
                    usernames.add(username)
                    emails.add(email)
                    users.append(User(full_name=fake.name(), username=username, email=email, password=hashed_password, bio=bio))
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

        initial_count = User.objects.count()
        # Bulk create all users in a single transaction
        with transaction.atomic():
            User.objects.bulk_create(users, ignore_conflicts=True)

        final_count = User.objects.count()

        # Count actually created users
        created_count = final_count - initial_count

        end_time = time.time()
        total_duration = end_time - start_time
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {created_count} fake users in {total_duration:.2f} seconds. '
            f'Average time per user: {(total_duration/created_count):.4f} seconds'
        ))
