from django.shortcuts import redirect, render, get_object_or_404
import logging
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Exists, OuterRef, BooleanField, Value
from django.contrib import messages
from django.urls import reverse
from blog_app.models import Blog, Tag
from django.contrib.auth import get_user_model

from profile_app.models import Follow
from utils.herlpers import pro_print

User = get_user_model()
logger = logging.getLogger(__name__)


def search(request):
    """
    Search posts, users and tags.
    Uses query param 'q' for search term.
    """
    q = request.GET.get("q", "")

    if not q.strip():
        messages.error(request, "Search term is required!")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

    try:
        base_query = (
            Blog.objects.select_related("author")
            .prefetch_related("tags")
            .only(
                "id",
                "title",
                "slug",
                "image",
                "content_preview",
                "created_at",
                "author__username",
                "author__full_name",
                "tags__name",
                "tags__slug",
                "tags__description",
            )
            .filter(
                Q(title__icontains=q)
                | Q(content__icontains=q)
                | Q(tags__name__icontains=q)
                | Q(author__username__icontains=q)
                | Q(author__full_name__icontains=q)
                | Q(author__email__icontains=q)
            )
            .distinct()
            .order_by("-created_at")
        )
        for_users = User.objects.filter(
            Q(username__icontains=q) | Q(full_name__icontains=q) | Q(email__icontains=q)
        ).distinct()
        for_tags = Tag.objects.filter(name__icontains=q)

        # If user is authenticated, add is_following field to for_users and for_tags
        if request.user.is_authenticated:
            for_users = (
                for_users.annotate(
                    is_following=Exists(
                        Follow.objects.filter(
                            follower=request.user, user=OuterRef("id")
                        )
                    )
                )
                .values(
                    "id",
                    "username",
                    "image",
                    "full_name",
                    "is_following",
                    "bio",
                    "tagline",
                )
                .distinct()
                .order_by("full_name")[:10]
            )
            for_tags = (
                for_tags.annotate(
                    is_following=Case(
                        When(tag_follows__user=request.user, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField(),
                    )
                )
                .annotate(
                    is_following=Case(
                        When(
                            tag_follows__user=request.user,
                            then=Value(True),
                        ),
                        default=Value(False),
                        output_field=BooleanField(),
                    )
                )
                .distinct()
                .values(
                    "id", "name", "slug", "description", "is_following", "description"
                )
                .order_by("name")[:10]
            )

    except Exception as e:
        logger.error(f"Error searching: {e}")
        messages.error(request, f"{e}")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

    # Pagination
    paginator = Paginator(base_query, 24)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "q": q,
        "for_posts": list(page_obj),
        "for_users": list(for_users),
        "for_tags": list(for_tags),
        "previous_page": (
            page_obj.previous_page_number() if page_obj.has_previous() else None
        ),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
    }
    return render(request, "blog_app/search.html", context)


def search_posts(request):
    """
    Search blog posts by title.
    Uses query param 'q' for search term.
    """
    q = request.GET.get("q", "")
    if not q.strip():
        messages.error(request, "Search term is required!")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

    try:
        posts = (
            Blog.objects.select_related("author")
            .filter(
                Q(title__icontains=q)
                | Q(content__icontains=q)
                | Q(tags__name__icontains=q)
                | Q(author__username__icontains=q)
                | Q(author__full_name__icontains=q)
                | Q(author__email__icontains=q)
            )
            .distinct()
            .only(
                "id",
                "title",
                "slug",
                "image",
                "content_preview",
                "created_at",
                "author__username",
                "author__full_name",
            )
        )

        posts = posts.order_by("-created_at")

    except Exception as e:
        logger.error(f"Error searching posts: {e}")
        messages.error(request, f"{e}")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

    # Pagination
    paginator = Paginator(posts, 24)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "posts": page_obj,
        "q": q,
        "previous_page": (
            page_obj.previous_page_number() if page_obj.has_previous() else None
        ),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
    }
    return render(request, "blog_app/search_posts.html", context)


def search_users(request):
    """
    Search users by username, full name or email.
    Uses query param 'q' for search term.
    """
    q = request.GET.get("q", "")

    if not q.strip():
        messages.error(request, "Search term is required!")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

    try:
        base_query = User.objects.filter(
            Q(username__icontains=q) | Q(full_name__icontains=q) | Q(email__icontains=q)
        ).distinct()

        if request.user.is_authenticated:
            users = base_query.annotate(
                is_following=Exists(
                    Follow.objects.filter(
                        follower=request.user,
                        user=OuterRef("pk"),
                    )
                )
            )

            users = users.values(
                "id",
                "image",
                "username",
                "full_name",
                "bio",
                "tagline",
                "is_following",
            ).order_by("full_name")
        else:
            users = (
                base_query.annotate(
                    is_following=Value(False, output_field=BooleanField()),
                )
                .values(
                    "id",
                    "username",
                    "image",
                    "full_name",
                    "is_following",
                )
                .order_by("full_name")
            )

    except Exception as e:
        logger.error(f"Error searching users: {e}")
        messages.error(request, f"{e}")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

    # Pagination
    paginator = Paginator(users, 24)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "users": list(page_obj),
        "q": q,
        "previous_page": (
            page_obj.previous_page_number() if page_obj.has_previous() else None
        ),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
    }
    return render(request, "blog_app/search_users.html", context)


def search_tags(request):
    """
    Search tags by name.
    Uses query param 'q' for search term.
    """
    try:
        q = request.GET.get("q", "")
        followed_tags = request.user.get_followed_tags().values_list("id", flat=True)
        tags = (
            Tag.objects.filter(name__icontains=q)
            .annotate(
                is_following=Case(
                    When(id__in=followed_tags, then=Value(True)),
                    output_field=BooleanField(),
                )
            )
            .order_by("name")
        )
    except Exception as e:
        logger.error(f"Error searching tags: {e}")
        messages.error(request, f"{e}")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

    # Pagination
    paginator = Paginator(tags, 24)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "tags": page_obj,
        "q": q,
        "previous_page": (
            page_obj.previous_page_number() if page_obj.has_previous() else None
        ),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
    }
    return render(request, "blog_app/search_tags.html", context)
