from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from utils.herlpers import pro_print
from django_ratelimit.core import is_ratelimited

User = get_user_model()


def user_login_required(redirect_url=None, error_message=None):
    """
    Decorator to ensure user is authenticated.
    Redirects to specified URL or referrer if not logged in.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            redirect_to = (
                redirect_url
                if redirect_url is not None
                else request.META.get("HTTP_REFERER", "blog:index")
            )
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(
                    request,
                    error_message or "You need to be logged in to perform this action.",
                )
                return redirect(redirect_to)

        return wrapped_view

    return decorator


def user_is_author(model, user_field, error_message=None):
    """
    Decorator to verify user owns/authored the object.
    Checks if requesting user matches specified user field.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, id, *args, **kwargs):
            try:
                obj = get_object_or_404(model, id=id)
                if (
                    not hasattr(obj, user_field)
                    or getattr(obj, user_field) != request.user
                ):
                    messages.warning(request, error_message or "Invalid request!")
                    return redirect(request.META.get("HTTP_REFERER", "blog:index"))
                else:
                    return view_func(request, id, *args, **kwargs)
            except Http404:
                messages.warning(request, error_message or "Invalid request!")
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))

        return wrapper

    return decorator


def custom_ratelimit(
    key="user", rate="2/h", method=None, group=None, error_message=None
):
    """
    Custom rate limit decorator with message handling
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Use the view function name as group if none provided
            group_id = group or view_func.__name__

            if is_ratelimited(
                request=request,
                group=group_id,
                key=key,
                rate=rate,
                method=method or ["POST"],
                increment=True,
            ):
                messages.error(
                    request,
                    error_message or "Too many attempts. Please try again in an hour.",
                )
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
