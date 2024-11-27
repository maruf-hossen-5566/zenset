from django.core.management.base import BaseCommand
from blog_app.models import Blog
from django.db.models import F, Q
import math


class Command(BaseCommand):
    help = "Updates likes count for all blogs"

    def handle(self, *args, **kwargs):
        for blog in Blog.objects.filter(
            Q(author__id="233c724d-9ae4-4877-9211-a4c848a24467")
            #   & Q(likes_count__gt=0)
        ):
            try:
                percentage = math.floor((90.0 / 100.0) * blog.likes_count)
                blog.likes_count = F("likes_count") - percentage
                blog.save(update_fields=["likes_count"])
            except Exception as error:
                self.stdout.write(self.style.ERROR(f"Error: {error}"))
