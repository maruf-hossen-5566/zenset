import cloudinary.uploader
from django.utils import timezone
import cloudinary
import datetime
import profile
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Case, When, F, Value, Count
from django.db.models.functions import Substr, Left
from django.contrib import messages
from django.urls import reverse
from blog_app.decorators import post_published_required
from blog_project_with_flowbite.decorators import (
    custom_ratelimit,
    user_is_author,
    user_login_required,
)
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from comment_app.models import Comment, Reply
from like_app.models import Like
from profile_app.models import Follow
from utils.herlpers import pro_print
from .models import Blog, Bookmark, Tag, TagFollow
from django.contrib.auth import get_user_model
from .forms import BlogForm
from django.db import transaction
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Prefetch
from django_ratelimit.decorators import ratelimit
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def index(request):
    """
    Homepage view.
    Show personalized and recommended posts.
    """
    page_number = request.GET.get("page", 1)
    user_id = request.user.id if request.user.is_authenticated else "anon"
    cache_key = f"blog:index:user_{user_id}:page_{page_number}"
    context = cache.get(cache_key)

    if not context:
        posts = Blog.objects.select_related("author").only(
            "id",
            "content_preview",
            "title",
            "slug",
            "created_at",
            "image",
            "is_published",
            "is_featured",
            # "author__id",
            "author__username",
            "author__full_name",
        )

        if request.user.is_authenticated:
            regular_posts = posts.exclude(
                Q(author=request.user) | Q(is_published=False) | Q(is_featured=True)
            )
            # Get followed tags
            followed_tags = request.user.get_followed_tags().values_list(
                "id", flat=True
            )
            if followed_tags:
                # Filter posts by followed tags
                followed_tags_posts = posts.filter(tags__id__in=followed_tags)
                regular_posts = regular_posts.union(followed_tags_posts)
        else:
            regular_posts = posts.filter(is_published=True, is_featured=False)

        try:
            featured_post = posts.filter(is_featured=True).earliest(
                "created_at"
            )  # .latest("created_at") can be used as well / for latest featured post
        except Blog.DoesNotExist:
            featured_post = None

        regular_posts = regular_posts.order_by("-created_at")

        # Do pagination
        paginator = Paginator(regular_posts, 24)
        page_obj = paginator.get_page(page_number)

        # Create the context
        context = {
            "featured_post": featured_post,
            "page_obj": list(page_obj),
            "previous_page": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        }
        cache.set(cache_key, context, 15 * 60)

    # Who to follow
    context["who_to_follow"] = (
        User.objects.exclude(
            Q(id=request.user.id) | Q(followers__follower=request.user)
        )
        .only("id", "username", "full_name", "bio")
        .values("id", "bio", "username", "full_name")[:9]
        if request.user.is_authenticated
        else User.objects.only("id", "username", "full_name", "bio").values(
            "id", "bio", "username", "full_name"
        )[:9]
    )
    # tags to follow
    context["tags_to_follow"] = (
        Tag.objects.exclude(tag_follows__user=request.user)
        .annotate(followers_count=Count("followers"))
        .order_by("-followers_count")[:9]
        if request.user.is_authenticated
        else Tag.objects.all().order_by("?")[:9]
    )

    return render(request, "blog_app/index.html", context)


@user_login_required(error_message="You need to be logged in to view this page.")
def following(request):
    """
    Following feed page.
    Shows posts from followed users and tags.
    """
    page_number = request.GET.get("page", 1)
    user_id = request.user.id if request.user.is_authenticated else "anon"
    cache_key = f"blog:following:user_{user_id}:page_{page_number}"
    context = cache.get(cache_key)

    if not context:
        posts = Blog.objects.select_related("author").only(
            "id",
            "content_preview",
            "title",
            "slug",
            "created_at",
            "image",
            "is_published",
            "author__username",
            "author__full_name",
        )

        if request.user.is_authenticated:
            posts = posts.filter(
                ~Q(author=request.user),
                is_published=True,
                author__followers__follower=request.user,
            )
        else:
            posts = posts.filter(is_published=True)

        posts = posts.order_by("-created_at")

        paginator = Paginator(posts, 24)
        page_obj = paginator.get_page(page_number)

        # Create the context
        context = {
            "page_obj": list(page_obj),
            "previous_page": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        }
        cache.set(cache_key, context, 24 * 60 * 60)

    context["who_to_follow"] = (
        User.objects.exclude(
            Q(id=request.user.id) | Q(followers__follower=request.user)
        )
        .only("id", "username", "full_name", "bio")
        .values("id", "bio", "username", "full_name")[:9]
        if request.user.is_authenticated
        else []
    )

    return render(request, "blog_app/following.html", context)


def trending(request):
    """
    Trending posts view.
    Shows popular posts based on likes and comments.
    """
    page_number = request.GET.get("page", 1)
    user_id = request.user.id if request.user.is_authenticated else "anon"
    cache_key = f"blog:trending:user_{user_id}:page_{page_number}"
    context = cache.get(cache_key)

    if not context:
        posts = Blog.objects.select_related("author").only(
            "id",
            "content_preview",
            "title",
            "slug",
            "created_at",
            "image",
            "is_published",
            "is_featured",
            "author__id",
            "author__username",
            "author__full_name",
        )

        if request.user.is_authenticated:
            posts = posts.exclude(author=request.user, is_published=False)
        else:
            posts = posts.filter(is_published=True)

        posts.order_by(
            "-views_count", "-likes_count", "-comments_count"
        )  # always order_by after filter, exclude, count and many more

        # Do pagination
        paginator = Paginator(posts, 24)
        page_obj = paginator.get_page(page_number)

        # Create the context
        context = {
            "page_obj": list(page_obj),
            "previous_page": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        }
        cache.set(cache_key, context, 30 * 60)

    return render(request, "blog_app/index.html", context)


def latest(request):
    """
    Latest posts view.
    Shows most recent posts.
    """
    page_number = request.GET.get("page", 1)
    user_id = request.user.id if request.user.is_authenticated else "anon"
    cache_key = f"blog:latest:user_{user_id}:page_{page_number}"
    context = cache.get(cache_key)

    if not context:
        base_query = Blog.objects.select_related("author").only(
            "id",
            "content_preview",
            "title",
            "slug",
            "created_at",
            "image",
            "is_published",
            "is_featured",
            "author__id",
            "author__username",
            "author__full_name",
        )

        if request.user.is_authenticated:
            posts = base_query.exclude(
                Q(author=request.user) | Q(is_published=False)
            ).order_by("-created_at")
        else:
            posts = base_query.filter(is_published=True).order_by("-created_at")

        # Do pagination
        paginator = Paginator(posts, 24)
        page_obj = paginator.get_page(page_number)

        # Create the context
        context = {
            "page_obj": list(page_obj),
            "previous_page": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        }
        cache.set(cache_key, context, 5 * 60)

    return render(request, "blog_app/latest.html", context)


@post_published_required
def post_detail(request, username, slug):
    """
    Blog post detail page.
    Shows full post content and engagement.
    """
    cache_key = f"blog:post_detail:user_{request.user.id if request.user.is_authenticated else 'anon'}:author_{username}:slug_{slug}"
    context = cache.get(cache_key)

    if not context:
        try:
            post = (
                Blog.objects.select_related("author")
                .prefetch_related(
                    # Prefetching comments and there replies
                    Prefetch(
                        "comments",
                        Comment.objects.select_related("user")
                        .prefetch_related(
                            Prefetch(
                                "replies",
                                Reply.objects.select_related(
                                    "user", "parent_reply", "parent_reply__user"
                                ).order_by("created_at"),
                            )
                        )
                        .annotate(eng=Count("replies"))
                        .order_by("-eng", "-created_at"),
                        "post_comments",
                    ),
                    # Prefetching Likes
                    Prefetch(
                        "likes",
                        (
                            Like.objects.filter(user=request.user)
                            if request.user.is_authenticated
                            else Like.objects.none()
                        ),
                        "liked",
                    ),
                    # Prefetching bookmarks
                    Prefetch(
                        "bookmarks",
                        (
                            Bookmark.objects.filter(user=request.user)
                            if request.user.is_authenticated
                            else Bookmark.objects.none()
                        ),
                        "bookmarked",
                    ),
                    # Prefetching tags
                    Prefetch("tags", Tag.objects.all(), "post_tags"),
                )
                .get(author__username=username, slug=slug)
            )

            following = (
                post.author.followers.filter(follower=request.user).exists()
                if request.user.is_authenticated and not request.user is post.author
                else False
            )

            related_posts = (
                Blog.objects.select_related("author")
                .filter(
                    Q(is_published=True) & Q(tags__in=post.tags.all())
                    | Q(author=post.author)
                )
                .exclude(id=post.id)
                .distinct()
                .only(
                    "id",
                    "title",
                    "slug",
                    "author__username",
                    "author__full_name",
                    "created_at",
                    "image",
                )[:6]
            )

            # If we need more posts to reach 6
            if related_posts.count() < 6:
                additional_posts = (
                    Blog.objects.filter(is_published=True)
                    .exclude(
                        Q(id=post.id)
                        | Q(id__in=related_posts.values_list("id", flat=True))
                    )
                    .only(
                        "id",
                        "title",
                        "slug",
                        "author__username",
                        "author__full_name",
                        "created_at",
                        "image",
                    )
                    .order_by("?")[: 6 - related_posts.count()]
                )
                related_posts = list(related_posts) + list(additional_posts)
        except Blog.DoesNotExist:
            messages.error(request, f"Post you are looking for does not exist!")
            return redirect(reverse("blog:index"))
        except Exception as error:
            messages.error(request, f"An error occurred: {error}")
            return redirect(reverse("blog:index"))

        context = {
            "post": post,
            "related_posts": related_posts,
            "liked": bool(post.liked),
            "bookmarked": bool(post.bookmarked),
            "following": bool(following),
            "comments": post.post_comments,
        }
        cache.set(cache_key, context, 15 * 60)

    return render(request, "blog_app/post_detail.html", context)


@user_login_required(redirect_url="blog:index")
@require_http_methods(["GET", "POST"])
@transaction.atomic
def create_post(request):
    """
    Create new blog post.
    Handles both draft and published states.
    """
    tags = Tag.objects.all()

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                post.created_at = timezone.now().date()

                # post.disable_comments = form.cleaned_data.get("disable_comments", False)
                # post.pin_to_profile = form.cleaned_data.get("pin_to_profile", False)

                post.save()
                form.save_m2m()
                messages.success(request, "Post published successfully.")
                return redirect(
                    reverse(
                        "blog:post_detail",
                        kwargs={"username": post.author.username, "slug": post.slug},
                    )
                )
            except Exception as error:
                messages.error(
                    request, f"An error occurred while saving the post: {error}"
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = BlogForm()
    return render(
        request,
        "blog_app/create_post.html",
        {"form": form, "tags": tags},
    )


@user_login_required()
@require_http_methods(["GET", "POST"])
@transaction.atomic
def create_draft_post(request):
    """
    Create draft blog post.
    User must be logged in.
    """
    tags = Tag.objects.all()[:25]

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user

                post.is_published = False

                post.created_at = datetime.datetime.now().date()
                post.save()
                form.save_m2m()
                messages.success(request, "Post saved successfully.")
                return redirect(
                    reverse(
                        "blog:post_detail",
                        kwargs={"username": post.author.username, "slug": post.slug},
                    )
                )
            except Exception as error:
                messages.error(
                    request, f"An error occurred while saving the post: {error}"
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = BlogForm()
    return render(
        request,
        "blog_app/create_post.html",
        {"form": form, "tags": tags},
    )


@custom_ratelimit(
    key="user",
    rate="10/h",
    method=["POST"],
    error_message="You are requesting too frequently. Please try again in an hour.",
)
@user_login_required(redirect_url="blog:index")
@require_http_methods(["GET", "POST"])
@transaction.atomic
def edit_post(request, id):
    """
    Edit existing blog post.
    User must be post author.
    """
    try:
        post = (
            request.user.blogs.select_related("author")
            .prefetch_related("tags")
            .only(
                "id",
                "title",
                "content",
                "image",
                "author__id",
                "tags__id",
                "tags__name",
                "is_published",
                "disable_comments",
                "pin_to_profile",
            )
            .get(id=id)
        )
    except Blog.DoesNotExist:
        messages.error(request, f"Page not found.")
        return redirect(request.META.get("HTTP_REFERER", "blog:index"))

    tags = Tag.objects.all()

    old_image = post.image
    if request.method == "POST":
        try:
            form = BlogForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                print(form.cleaned_data)
                post = form.save(commit=False)
                if request.POST.get("draft"):
                    post.is_published = False

                post.save()
                form.save_m2m()
                new_image = form.cleaned_data.get("image")
                if new_image and old_image and new_image != old_image:
                    # Delete old image from Cloudinary
                    cloudinary.uploader.destroy(public_id=old_image.public_id)
                messages.success(request, "Post updated successfully.")
                return redirect(
                    reverse(
                        "blog:post_detail",
                        kwargs={"username": post.author.username, "slug": post.slug},
                    )
                )

            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")

        except Exception as error:
            messages.error(request, f"An error occurred: {error}")
    else:
        form = BlogForm(instance=post)

    context = {
        "form": form,
        "post": post,
        "tags": tags,
    }
    return render(request, "blog_app/edit_post.html", context)


@require_GET
def bookmark(request, id):
    """
    Bookmark/Unbookmark a post.
    User must be logged in.
    """
    logger.info(
        f"User {request.user.username} attempting to bookmark/unbookmark post {id}"
    )
    try:
        blog = get_object_or_404(Blog, id=id)

        obj, created = Bookmark.objects.get_or_create(user=request.user, blog=blog)
        if created:
            logger.info(f"User {request.user.username} bookmarked post {blog.title}")
            messages.success(request, "Post bookmarked successfully.")
        else:
            logger.info(
                f"User {request.user.username} removed bookmark from post {blog.title}"
            )
            obj.delete()
            messages.success(request, "Post removed from bookmarked.")
        return redirect(
            request.META.get(
                "HTTP_REFERER",
                reverse(
                    "blog:post_detail",
                    kwargs={"username": blog.author.username, "slug": blog.slug},
                ),
            )
            or reverse("blog:index")
        )
    except Blog.DoesNotExist:
        logger.error(f"Failed bookmark attempt - Post {id} not found")
        messages.error(request, "Post not found!")
    except Exception as error:
        logger.error(f"Error in bookmark view: {error}", exc_info=True)
        messages.error(request, f"An error occurred: {error}")

    return redirect(request.META.get("HTTP_REFERER", "blog:index"))


@user_login_required()
@require_GET
def disable_comments(request, id):
    """
    Enable/disable post comments.
    User must be post author.
    """
    try:
        post = request.user.blogs.get(id=id)
        post.disable_comments = not post.disable_comments
        post.save(update_fields=["disable_comments"])
        if post.disable_comments:
            messages.success(request, "Comments disabled successfully.")
        else:
            messages.success(request, "Comments enabled successfully.")

        # return redirect(
        #     request.META.get(
        #         "HTTP_REFERER",
        #         reverse(
        #             "blog:post_detail",
        #             kwargs={"username": post.author.username, "slug": post.slug},
        #         ),
        #     )
        #     or reverse("blog:index")
        # )
    except Blog.DoesNotExist:
        messages.error(request, "Blog not fount!")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

    return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))


@user_login_required()
@require_GET
def change_post_status(request, id):
    """
    Change post status (draft/published).
    User must be post author.
    """
    try:
        post = request.user.blogs.get(id=id)
        post.is_published = not post.is_published
        post.save(update_fields=["is_published"])
        messages.success(request, "Post status changed successfully.")
    except Blog.DoesNotExist:
        messages.error(request, "Blog not found!")
    except Exception as error:
        messages.error(
            request, f"An error occurred while changing the post status: {error}"
        )

    return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))


# --- TAG
@user_login_required(redirect_url="blog:index")
@require_GET
@transaction.atomic
def tag_detail(request, slug):
    """
    Tag detail view.
    Shows posts with this tag.
    """
    page_number = request.GET.get("page", 1)
    user_id = request.user.id if request.user.is_authenticated else "anon"
    cache_key = f"blog:tag:user_{user_id}:slug_{slug}:page_{page_number}"
    context = cache.get(cache_key)

    if not context:
        try:
            tag = get_object_or_404(Tag, slug=slug)
            if tag:
                posts = (
                    Blog.objects.filter(tags=tag, is_published=True)
                    .select_related("author")
                    .only(
                        "id",
                        "title",
                        "slug",
                        "content_preview",
                        "created_at",
                        "image",
                        "author__id",
                        "author__username",
                        "author__image",
                        "author__full_name",
                    )
                )
                posts = posts.order_by("-created_at")
            else:
                posts = []
        except Http404:
            messages.error(request, f"Tag not found!")
            return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))
        except Exception as error:
            messages.error(request, f"{error}")
            return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

        paginator = Paginator(posts, 24)
        page_obj = paginator.get_page(page_number)
        context = {
            "page_obj": list(page_obj),
            "tag": tag,
            "previous_page": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "next_page": (page_obj.next_page_number() if page_obj.has_next() else None),
        }
        cache.set(cache_key, context, 300)

    return render(request, "blog_app/tags_detail.html", context)


@user_login_required(redirect_url="blog:index")
@require_GET
@transaction.atomic
def follow_tag(request, id):
    """
    Follow/unfollow a tag.
    User must be logged in.
    """
    user = request.user
    logger.info(f"User {user.username} attempting to follow/unfollow tag {id}")
    try:
        tag = get_object_or_404(Tag, id=id)
        if tag.is_followed_by(user):
            tag.unfollow(user)
            logger.info(f"User {user.username} unfollowed tag {tag.name}")
            messages.success(
                request,
                f"You are no longer following <span class='font-semibold text-blue-600'>{tag.name}</span> tag.",
            )
        else:
            tag.follow(user)
            logger.info(f"User {user.username} followed tag {tag.name}")
            messages.success(
                request,
                f"You are now following <span class='font-semibold text-blue-600'>{tag.name}</span> tag.",
            )
    except Exception as error:
        logger.error(f"Error in follow_tag view: {error}", exc_info=True)
        messages.error(request, f"{error}")

    return redirect(
        request.META.get("HTTP_REFERER", "blog:index") or reverse("blog:index")
    )


# --- DELETE
@user_login_required()
@require_GET
@user_is_author(Blog, "author")
@transaction.atomic
def delete_post(request, id):
    """
    Delete a blog post.
    User must be post author.
    """
    logger.info(f"User {request.user.username} attempting to delete post {id}")
    try:
        post = request.user.blogs.get(id=id)
        post_detail_url = reverse(
            "blog:post_detail",
            kwargs={"username": post.author.username, "slug": post.slug},
        )
        logger.info(f"Deleting post: {post.title} by {post.author.username}")
        post.delete()
        logger.info(f"Post {id} successfully deleted by {request.user.username}")
        messages.success(request, "Post deleted successfully.")
    except Exception as error:
        logger.error(f"Error deleting post {id}: {error}", exc_info=True)
        messages.error(request, f"An error occurred while deleting the post: {error}")

    if "/dashboard/" in request.META.get("HTTP_REFERER", ""):
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))
    return redirect(reverse("blog:index"))
