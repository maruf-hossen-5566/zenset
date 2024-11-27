from django.db import models
from blog_app.models import Blog
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


class Like(models.Model):
    """
    Store likes on blog posts.
    Links users to the posts they've liked.
    """
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user.username} on {self.blog.title}"
