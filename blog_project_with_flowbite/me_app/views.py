from datetime import datetime, timedelta
import cloudinary.uploader
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, BooleanField
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import Cast
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.core.cache import cache
import requests
from user_sessions.models import Session
from auth_app.forms import ProfileForm
from blog_project_with_flowbite.decorators import user_login_required
from utils.herlpers import pro_print
from django.views.decorators.http import require_POST, require_http_methods, require_GET
import cloudinary


@user_login_required(redirect_url="blog:index")
def index(request):
    """
    User dashboard home.
    Shows user stats and recent activity.
    """
    try:
        user = request.user
        total_posts = user.blogs.filter(is_published=True).count()
        latest_post = user.blogs.filter(is_published=True).order_by("-created_at")[:5]
        draft_posts = user.blogs.filter(is_published=False).order_by("-created_at")[:5]
        pending_posts = user.blogs.filter(is_published=False).count()
        total_views_and_engagement = user.blogs.aggregate(
            views=Sum("views_count"),
            likes=Sum("likes_count"),
            comments=Sum("comments_count"),
        )
        total_blogs = user.blogs.count()

        top_performing_posts = user.blogs.annotate(
            engagement_score=F("views_count")
            + F("likes_count") * 2
            + F("comments_count") * 3
        ).order_by("-engagement_score")[:5]

    except Exception as error:
        messages.error(request, f"An error occurred: {error}")
        return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

    context = {
        "total_posts": total_posts,
        "latest_posts": latest_post,
        "total_views_and_engagement": total_views_and_engagement,
        "draft_posts": draft_posts,
        "pending_posts": pending_posts,
        "top_performing_posts": top_performing_posts,
    }
    return render(request, "me_app/dashboard.html", context)


@user_login_required(redirect_url="blog:index")
def posts(request):
    """
    User's posts page.
    Shows all posts by the user.
    """
    # posts_list = request.user.blogs.all()
    posts_list = request.user.blogs.select_related("author").only(
        "id",
        "author__id",
        "author__username",
        "title",
        "slug",
        "image",
        "disable_comments",
        "created_at",
        "is_published",
        "published_date",
        "views_count",
        "likes_count",
        "comments_count",
    )

    # Apply search filter
    search_query = request.GET.get("search", "")
    if search_query.strip():
        posts_list = posts_list.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    # Apply status filter
    status_filter = request.GET.get("publish", "")
    if status_filter:
        is_published = status_filter.lower() == "true"  # Convert string to boolean
        posts_list = posts_list.filter(is_published=is_published)

    # Apply sorting
    sort = request.GET.get("sort", "")
    if sort == "date_desc":
        posts_list = posts_list.order_by("-created_at")
    elif sort == "date_asc":
        posts_list = posts_list.order_by("created_at")
    elif sort == "views_desc":
        posts_list = posts_list.order_by("-views_count")
    elif sort == "likes_desc":
        posts_list = posts_list.order_by("-likes_count")
    elif sort == "comments_desc":
        posts_list = posts_list.order_by("-comments_count")
    else:
        # Default sorting
        posts_list = posts_list.order_by("-created_at")

    # Pagination
    paginator = Paginator(posts_list, 10)  # Show 10 posts per page
    page = request.GET.get("page")
    posts = paginator.get_page(page)

    # Store all query parameters
    query_params = request.GET.copy()

    if "page" in query_params:
        del query_params["page"]  # Remove page from query params

    # Store query string for pagination
    query_string = query_params.urlencode()

    context = {
        "posts": posts,
        "query_string": query_string,  # Add query string to context
    }
    return render(request, "me_app/posts.html", context)


@user_login_required(redirect_url="blog:index")
def following(request):
    """
    Following page.
    Shows authors and tags user follows.
    """
    user = request.user
    following = user.following.values(
        username=F("user__username"),
        full_name=F("user__full_name"),
        pk=F("user__id"),
        since=F("created_at"),
    ).order_by("-created_at")

    context = {
        "header": "Following",
        "following": following,
    }
    return render(request, "me_app/following.html", context)


@user_login_required(redirect_url="blog:index")
def followers(request):
    """
    Followers page.
    Shows user's followers.
    """
    user = request.user
    following_ids = set(user.following.values_list("user__id", flat=True))
    followers = user.followers.annotate(
        is_following=Case(
            When(Q(follower__id__in=following_ids), then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    ).values(
        "is_following",
        full_name=F("follower__full_name"),
        username=F("follower__username"),
        pk=F("follower__id"),
        since=F("created_at"),
    )

    context = {"header": "Followers", "followers": followers}
    return render(request, "me_app/followers.html", context)


@user_login_required(redirect_url="blog:index")
def tags(request):
    """
    Tags page.
    Shows tags user follows.
    """
    user = request.user
    tags = user.get_followed_tags()
    tags = tags.annotate(
        is_following=Case(
            When(tag_follows__user=user, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    )
    pro_print(tags, "TAG")

    context = {
        "tags": tags,
    }
    return render(request, "me_app/tags.html", context)


@user_login_required(redirect_url="blog:index")
def bookmarks(request):
    """
    Bookmarks page.
    Shows posts user has bookmarked.
    """
    bookmarks = request.user.bookmarks.order_by("-created_at")
    context = {
        "bookmarks": bookmarks,
    }
    return render(request, "me_app/bookmarks.html", context)


@user_login_required(redirect_url="blog:index")
def analytics(request):
    """
    Analytics page.
    Shows post and profile stats.
    """
    user = request.user
    time_range = int(request.GET.get("time_range", 6))

    # Adjust time ranges
    if time_range == 30:
        time_range = 30  # 30 + 1
    elif time_range == 90:
        time_range = 90  # 90 + 1
    elif time_range == 365:
        time_range = 365  # 365 + 1
    else:
        time_range = 6  # 7 + 1

    end_date = timezone.now().date()  # Get just the date
    start_date = end_date - timezone.timedelta(days=time_range)
    pro_print(start_date, "S")
    pro_print(end_date, "E")

    # Get daily views data with explicit date range
    views_data = (
        user.blogs.filter(created_at__range=[start_date, end_date])
        .values("created_at")
        .annotate(
            daily_views=Sum("views_count"),
            daily_likes=Sum("likes_count"),
            daily_comments=Sum("comments_count"),
        )
        .order_by("-created_at")
    )

    # Generate all dates in range with zero-filling
    views_list = []
    dates_list = []
    current_date = start_date

    # Convert views_data to dictionary for easier lookup
    views_dict = {
        entry["created_at"]: {
            "views": entry["daily_views"] or 0,
            "likes": entry["daily_likes"] or 0,
            "comments": entry["daily_comments"] or 0,
        }
        for entry in views_data
    }

    # Fill in all dates
    while current_date <= end_date:
        dates_list.append(current_date.strftime("%Y-%m-%d"))
        daily_stats = views_dict.get(current_date, {"views": 0})
        views_list.append(daily_stats["views"])
        current_date += timedelta(days=1)

    # Total stats (existing code)
    stats_overview = user.blogs.aggregate(
        total_views=Sum("views_count"),
        total_likes=Sum("likes_count"),
        total_comments=Sum("comments_count"),
    )

    total_blogs = user.blogs.count()

    # Popular tags
    popular_tags = (
        user.blogs.values("tags__name")
        .annotate(
            count=Count("tags__name"),
            percentage=ExpressionWrapper(
                Cast(Count("tags__name"), FloatField()) * 100.0 / total_blogs,
                output_field=FloatField(),
            ),
        )
        .values("tags__name", "count", "percentage")
        .order_by("-count")[:5]
    )

    # Top performing posts
    top_posts = (
        user.blogs.select_related("author")
        .only(
            "id",
            "author__id",
            "author__username",
            "title",
            "slug",
            "views_count",
            "likes_count",
            "comments_count",
            "published_date",
        )
        .annotate(
            engagement_rate=ExpressionWrapper(
                (F("likes_count") + F("comments_count"))
                * 100.0
                / (F("views_count") + 1),
                output_field=FloatField(),
            )
        )
        .order_by("-engagement_rate")[:5]
    )

    context = {
        "stats_overview": stats_overview,
        "views_data": views_list,
        "views_date": dates_list,
        "top_posts": top_posts,
        "popular_tags": popular_tags,
    }

    return render(request, "me_app/analytics.html", context)


@user_login_required(redirect_url="blog:index")
@require_http_methods(["GET", "POST"])
@transaction.atomic
def profile(request):
    """
    Profile settings page.
    Update profile info and avatar.
    """
    user = request.user
    old_image = user.image

    if request.method == "POST":
        if not request.POST.get("full_name"):
            messages.error(request, "Full name is required.")
            return redirect(reverse("dashboard:profile_settings"))

        # try:
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            if request.FILES.get("image") is not None:
                # Delete old image from Cloudinary
                if old_image:
                    cloudinary.uploader.destroy(public_id=old_image.public_id)

            messages.success(request, "Profile updated successfully.")
            return redirect(reverse("dashboard:profile_settings"))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{str(error)}")
            return redirect(reverse("dashboard:profile_settings"))
        # except Exception as error:
        #     messages.error(request, f"An error occurred: {str(error)}")
        #     return redirect(reverse("dashboard:profile_settings"))

    context = {
        "user": user,
    }
    return render(request, "me_app/profile.html", context)


@user_login_required(redirect_url="blog:index")
def security(request):
    """
    Security settings page.
    Manage password and sessions.
    """
    try:
        user = request.user
        sessions = request.user.session_set.filter(expire_date__gt=datetime.now())[:10]
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")
        return redirect(request.META.get("HTTP_REFERER") or reverse("dashboard:index"))

    context = {
        "page_title": "Account Security",
        "page_subtitle": "Manage your account security settings and preferences",
        "sessions": sessions,
        "sessions_count": sessions.count(),
    }
    return render(request, "me_app/security.html", context)


@user_login_required(redirect_url="blog:index")
@require_POST
def delete_session(request, session_key):
    """
    End a specific session.
    User must be logged in.
    """
    try:
        session = request.user.session_set.get(session_key=session_key)
        session.delete()
    except Session.DoesNotExist:
        messages.error(request, f"Invalid session key.")
        return redirect(
            request.META.get("HTP_REFERER", "blog:index"), reverse("blog:index")
        )
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")
    return redirect(reverse("dashboard:security_settings") or reverse("blog:index"))


@user_login_required(redirect_url="blog:index")
@require_http_methods(["POST"])
def terminate_sessions(request):
    """
    End all other sessions.
    User must be logged in.
    """
    try:
        session_key = request.session.session_key
        session = request.user.session_set.filter(~Q(session_key=session_key))
        session.delete()
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")
    return redirect(
        request.META.get("HTTP_REFERER", reverse("dashboard:security_settings"))
    )


@user_login_required(redirect_url="blog:index")
@require_GET
def email_settings(request):
    """
    Email settings page.
    Toggle email notifications.
    """
    return render(request, "me_app/email_settings.html")
