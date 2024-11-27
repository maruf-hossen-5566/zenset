from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Exists, OuterRef, BooleanField, Value
from django.contrib import messages
from blog_app.models import Blog, Tag
from django.contrib.auth import get_user_model

from profile_app.models import Follow
from utils.herlpers import pro_print

User = get_user_model()


# def search(request):
#     q = request.GET.get("q", "")

#     title_query = Blog.objects.filter(title__icontains=q)
#     content_query = Blog.objects.filter(content__icontains=q)
#     category_query = Blog.objects.filter(category__name__icontains=q)
#     tag_query = Blog.objects.filter(tags__name__icontains=q)
#     author_username_query = Blog.objects.filter(author__username__icontains=q)
#     author_fullname_query = Blog.objects.filter(author__full_name__icontains=q)
#     author_email_query = Blog.objects.filter(author__email__icontains=q)

#     for_posts = title_query.union(
#         content_query,
#         category_query,
#         tag_query,
#         author_username_query,
#         author_fullname_query,
#         author_email_query,
#     )[:18]

#     for_users = User.objects.filter(
#         Q(username__icontains=q) | Q(full_name__icontains=q) | Q(email__icontains=q)
#     )[:10]
#     for_categories = Category.objects.filter(name__icontains=q)[:10]
#     for_tags = Tag.objects.filter(name__icontains=q)[:10]

#     context = {
#         "q": q,
#         "for_posts": for_posts,
#         "for_users": for_users,
#         "for_categories": for_categories,
#         "for_tags": for_tags,
#     }
#     return render(request, "blog_app/search.html", context)


def search(request):
    """
    Search posts, users and tags.
    Uses query param 'q' for search term.
    """
    q = request.GET.get("q", "")

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
        )[:30]
    )

    for_users = User.objects.filter(
        Q(username__icontains=q) | Q(full_name__icontains=q) | Q(email__icontains=q)
    )[:10]
    for_tags = Tag.objects.filter(name__icontains=q)[:10]

    context = {
        "q": q,
        "for_posts": base_query,
        "for_users": for_users,
        "for_tags": for_tags,
    }
    return render(request, "blog_app/search.html", context)


def search_posts(request):
    """
    Search blog posts by title.
    Uses query param 'q' for search term.
    """
    q = request.GET.get("q", "")

    posts = (
        Blog.objects.select_related("author")
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
        .filter(title__icontains=q)[:50]
    )
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
    users = User.objects.filter(
        Q(username__icontains=q) | Q(full_name__icontains=q) | Q(email__icontains=q)
    ).annotate(
        is_following=Case(
            When(followers__follower=request.user, then=Value(True)),
            output_field=BooleanField(),
        )
    )
    # Pagination
    paginator = Paginator(users, 24)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "users": page_obj,
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
    q = request.GET.get("q", "")
    followed_tags = request.user.get_followed_tags().values_list("id", flat=True)
    pro_print(followed_tags, "F TAGS")
    tags = Tag.objects.filter(name__icontains=q).annotate(
        is_following=Case(
            When(id__in=followed_tags, then=Value(True)),
            output_field=BooleanField(),
        )
    )

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
