from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.urls import reverse
from blog_app.decorators import (
    block_self_like,
    post_published_required,
    post_published_required_for_engagement,
)
from blog_app.models import Blog
from blog_project_with_flowbite.decorators import user_login_required
from like_app.models import Like
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@user_login_required()
@require_http_methods(["GET"])
@post_published_required_for_engagement
@block_self_like
@transaction.atomic
def like_post(request, id):
    """
    Toggle like on a blog post.
    User must be logged in and can't like their own post.
    """
    try:
        blog = get_object_or_404(Blog, id=id)
        like_obj, created = Like.objects.get_or_create(
            blog=blog,
            user=request.user,
        )

        if created:
            blog.increment_like()
        else:
            blog.decrement_like()
            like_obj.delete()
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")

    return redirect(
        reverse(
            "blog:post_detail",
            kwargs={"username": blog.author.username, "slug": blog.slug},
        )
        or request.META.get("HTTP_REFERER", "blog:index")
    )
