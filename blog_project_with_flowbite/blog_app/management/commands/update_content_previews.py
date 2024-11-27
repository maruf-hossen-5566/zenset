from django.core.management.base import BaseCommand
from blog_app.models import Blog
from django.utils.html import strip_tags

class Command(BaseCommand):
    help = 'Updates content previews for existing blog posts'

    def handle(self, *args, **options):
        blogs = Blog.objects.all()
        for blog in blogs:
            if not blog.content_preview and blog.content:
                blog.content_preview = strip_tags(blog.content)[:200]
                blog.save(update_fields=['content_preview'])
                self.stdout.write(f'Updated preview for blog: {blog.id}') 