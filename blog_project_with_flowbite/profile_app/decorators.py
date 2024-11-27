from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

def cannot_follow_yourself(view_func):
    """
    Decorator to prevent users from following themselves.
    Redirects with warning message if attempted.
    """
    @wraps(view_func)
    def wrapper(request, user_id, *args, **kwargs):
        if request.user.id == user_id:
            messages.warning(request, 'You cannot follow yourself!')
            return redirect(request.META.get('HTTP_REFERER', 'blog:index'))
        else:
            return view_func(request, user_id, *args, **kwargs)
    return wrapper
