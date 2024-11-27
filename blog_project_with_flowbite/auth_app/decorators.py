from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from functools import wraps


def anonymous_required(view_func):
    """
    Decorator to restrict authenticated users from accessing a view.
    Redirects to homepage if user is already logged in.
    """

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in!")
            return redirect(reverse("blog:index"))
        return view_func(request, *args, **kwargs)

    return wrapped_view
