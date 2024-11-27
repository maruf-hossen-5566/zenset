from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import get_user_model
from blog_app.models import Blog
from blog_project_with_flowbite.decorators import user_login_required
from profile_app.decorators import cannot_follow_yourself
from profile_app.models import Follow
from django.core.cache import cache

User = get_user_model()


def profile(request, username):
    """
    User profile page.
    Shows user info and published posts.
    """
    user_id = request.user.id if request.user.is_authenticated else "anon"
    page_number = request.GET.get("page", 1)
    cache_key = f"profile_of_{username}__for_user_{user_id}_page_{page_number}"
    context = cache.get(cache_key)
    try:
        user = get_object_or_404(User, username=username)
    except Http404:
        messages.error(request, "User you are looking for does not exist!")
        return redirect(request.META.get("HTTP_REFERER", "blog:index"))

    if not context:
        try:
            base_query = user.blogs.only(
                "id",
                "author__id",
                "author__full_name",
                "created_at",
                "title",
                "published_date",
                "is_published",
                "slug",
                "content_preview",
            )
            posts = base_query.filter(is_published=True).order_by("-created_at")

            page_obj = Paginator(posts, 24)
            page_obj = page_obj.page(page_number)

        except Http404:
            messages.error(request, "User you are looking for does not exist!")
            return redirect(request.META.get("HTTP_REFERER", "blog:index"))
        except Exception as error:
            messages.error(request, f"An error occurred: {error}")
            return redirect(request.META.get("HTTP_REFERER", "blog:index"))

        context = {
            "user": user,
            "posts": list(page_obj),
            "previous_page": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        }
        cache.set(cache_key, context, timeout=60)

    context["following"] = (
        user.followers.filter(follower=request.user).exists()
        if request.user.is_authenticated
        else False
    )
    return render(request, "profile_app/profile.html", context)


@user_login_required(redirect_url="auth:login")
@cannot_follow_yourself
@transaction.atomic
def follow(request, user_id):
    """
    Follow/unfollow action.
    Toggles following status for target user.
    """
    try:
        user = get_object_or_404(User, id=user_id)
        obj, created = Follow.objects.get_or_create(user=user, follower=request.user)

        if created:
            messages.success(
                request,
                f"You are now following <span class='font-semibold text-blue-600'>{user.full_name}</span>",
            )
        else:
            obj.delete()
            messages.success(
                request,
                f"Unfollowed <span class='font-semibold text-blue-600'>{user.full_name}</span>",
            )

    except Exception as error:
        messages.error(request, f"An error occurred: {error}")

    return redirect(request.META.get("HTTP_REFERER", "blog:index"))
