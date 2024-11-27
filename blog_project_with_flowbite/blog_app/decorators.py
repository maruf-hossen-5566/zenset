from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

from blog_app.models import Blog
from comment_app.models import Comment, Reply

User = get_user_model()


def post_published_required(view_func):
    """
    Decorator to ensure blog post is published.
    Only allows author to view unpublished posts.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            username = kwargs.get("username")
            slug = kwargs.get("slug")
            post = get_object_or_404(Blog, author__username=username, slug=slug)
            if not post.is_published and post.author != request.user:
                messages.error(request, "Page not found!")
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))
            else:
                return view_func(request, *args, **kwargs)

        except Blog.DoesNotExist:
            messages.error(request, "Post not found!")
            return redirect("blog:index")
        except Exception as error:
            messages.error(request, f"An error occurred: {error}")
            return redirect("blog:index")

    return wrapper


def post_published_required_for_engagement(view_func):
    """
    Decorator to ensure post is published before allowing engagement.
    Blocks actions like comments and likes on unpublished posts.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            id = kwargs.get("id")
            post = get_object_or_404(Blog, id=id)
            if not post.is_published:
                if post.author == request.user:
                    messages.error(
                        request,
                        "Post needs to be published first to perform this action!",
                    )
                else:
                    messages.error(request, "Page not found!")

                return redirect(request.META.get("HTTP_REFERER", "blog:index"))
            else:
                return view_func(request, *args, **kwargs)

        except Blog.DoesNotExist:
            messages.error(request, "Post not found!")
            return redirect(request.META.get("HTTP_REFERER", "blog:index"))
        except Exception as error:
            messages.error(request, f"An error occurred: {error}")
            return redirect(request.META.get("HTTP_REFERER", "blog:index"))

    return wrapper


def block_self_like(view_func):
    """
    Decorator to prevent authors from liking their own posts.
    Redirects with warning message if attempted.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            id = kwargs.get("id")
            post = get_object_or_404(Blog, id=id)
            if post.author == request.user:
                messages.warning(request, "Author cannot like their own post!")
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))
            else:
                return view_func(request, *args, **kwargs)
        except Blog.DoesNotExist:
            messages.error(request, "Post not found!")
            return redirect(request.META.get("HTTP_REFERER", "blog:index"))
        except Exception as error:
            messages.error(request, f"An error occurred: {error}")
            return redirect(request.META.get("HTTP_REFERER", "blog:index"))

    return wrapper
