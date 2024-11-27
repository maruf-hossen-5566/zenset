from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Count
from blog_project_with_flowbite.decorators import user_is_author, user_login_required
from notification_app.models import Notification
from django.db import transaction
from django.core.cache import cache
from django.core.paginator import Paginator


@user_login_required()
def index(request):
    """
    Show user's notifications.
    Supports filtering and pagination.
    """

    filter_type = request.GET.get("filter", "all")
    page_number = request.GET.get("page", 1)
    cache_key = (
        f"notification:user_{request.user.id}:page_{page_number}:filter_{filter_type}"
    )
    context = cache.get(cache_key)

    if not context:
        try:
            notifications = request.user.notifications.select_related(
                "user", "from_user", "post", "post__author"
            ).only(
                # Notification fields
                "id",
                "type",
                "read",
                "post__title",
                "post__slug",
                "created_at",
                # User fields
                "user__full_name",
                "user__username",
                "user__image",
                # From user fields
                "from_user__full_name",
                "from_user__username",
                "from_user__image",
                # Post fields
                "post__title",
                "post__slug",
                "post__author__username",
                "post__author__image",
                "post__author__full_name",
            )

            if filter_type and filter_type != "all":
                notifications = notifications.filter(type=filter_type)

            notifications.filter(read=False).update(read=True)
            request.user.unread_notifications = 0
            request.user.save()

            notifications = notifications.order_by("-created_at")

        except Exception as error:
            messages.error(request, f"An error occurred: {error}")

        paginator = Paginator(notifications, 24)
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": list(page_obj),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            "previous_page": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "filter": filter_type,
            "total_count": page_obj.paginator.count,
        }
        cache.set(cache_key, context, 60 * 5)

    return render(request, "notification_app/index.html", context)


@user_login_required()
@transaction.atomic
def delete(request, id):
    """
    Delete a notification which belongs to the user.
    User must be logged in.
    """
    try:
        user = request.user
        obj = user.notifications.get(id=id)
        obj.delete()
        messages.success(request, "Notification deleted successfully.")
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")

    return redirect(request.META.get("HTTP_REFERER", "blog:index"))


@user_login_required()
@transaction.atomic
def delete_all(request):
    """
    Delete all notifications which belong to the user.
    User must be logged in.
    """
    try:
        user = request.user
        objs = user.notifications.all()
        objs.delete()
        messages.success(request, "Notifications are deleted successfully.")
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")

    return redirect(request.META.get("HTTP_REFERER", "blog:index"))
