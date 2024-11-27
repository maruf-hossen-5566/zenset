from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError, transaction
from auth_app.decorators import anonymous_required
from auth_app.forms import RegisterForm
from blog_project_with_flowbite import settings
from blog_project_with_flowbite.decorators import custom_ratelimit, user_login_required
from email_app.services import EmailService
from utils.herlpers import pro_print
from django.views.decorators.http import require_http_methods, require_GET
from django.urls import reverse
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model


User = get_user_model()


@anonymous_required
@ratelimit(key="ip", rate="5/m", method=["POST"])
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Login page view.
    Rate limited to 5 attempts per minute.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect(reverse("blog:index"))
        else:
            messages.error(request, "Invalid credentials!")
    return render(request, "auth_app/login.html")


@anonymous_required
@ratelimit(key="ip", rate="5/m", method=["POST"])
@require_http_methods(["GET", "POST"])
@transaction.atomic
def register_view(request):
    """
    Registration page view.
    Rate limited to 5 attempts per minute.
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                new_user = form.save()

                if new_user:
                    login(request, new_user)
                    EmailService.send_welcome_email(new_user.email, new_user.username)
                    messages.success(request, "Account created successfully!")
                    return redirect(reverse("blog:index"))
                else:
                    messages.error(
                        request, "Failed to create account. Please try again."
                    )
            except Exception as e:
                # messages.error(request, f"Failed to create account, please try again.")
                messages.error(request, f"An error occurred: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

    return render(request, "auth_app/register.html")


@user_login_required()
@require_GET
def logout_view(request):
    """
    Logout the user.
    Redirects to login page.
    """
    cache_key = f"home_page_context_{str(request.user.id) if request.user.is_authenticated else 'anonymous'}"
    logout(request)
    cache.delete(cache_key)
    return redirect(settings.LOGOUT_REDIRECT_URL)


# @custom_ratelimit(key="ip", rate="2/h", method=["POST"])
@user_login_required()
@require_http_methods(["GET", "POST"])
@transaction.atomic
def change_pass(request):
    """
    Change password page.
    User must be logged in.
    """
    if request.method == "POST":
        user = request.user
        try:
            old_pass = request.POST.get("old_pass", "")
            new_pass = request.POST.get("new_pass", "")
            new_pass_2 = request.POST.get("new_pass_2", "")

            if not old_pass.strip() or not new_pass.strip() or not new_pass_2.strip():
                messages.error(request, "Fill the fields properly.")
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))

            if new_pass != new_pass_2:
                messages.error(request, "New passwords didn't match.")
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))

            validate_pass = check_password(str(old_pass), str(user.password))
            if validate_pass:
                validate_password(new_pass)
                user.set_password(new_pass)
                user.save()
                logout(request)
                messages.success(
                    request,
                    "Password changed successfully. Please login with your new password.",
                )
                return redirect(reverse("auth:login") or reverse("blog:index"))
            else:
                messages.error(request, "Current password is incorrect!")

        except ValidationError as error:
            for message in error.messages:
                messages.error(request, f"{message}")
        except Exception as error:
            messages.error(request, f"An error occurred: {error}")

        return redirect(request.META.get("HTTP_REFERER", "blog:index"))

    return render(request, "auth_app/change_pass.html")


@user_login_required()
@require_http_methods(["GET", "POST"])
def delete_account(request):
    """
    Delete user account page.
    User must be logged in.
    """
    user = request.user
    typed = request.POST.get("type", "")

    if typed.strip().lower() != "delete":
        messages.error(request, "Please type 'DELETE' to confirm account deletion.")
        return redirect(request.META.get("HTTP_REFERER", "blog:index"))
    try:
        logout(request)
        user.delete()
        return redirect(settings.LOGOUT_REDIRECT_URL)
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")
        return redirect(request.META.get("HTTP_REFERER", "blog:index"))


# --- Account recovery


@custom_ratelimit(key="ip", rate="2/h", method=["POST"])
@require_http_methods(["GET", "POST"])
@transaction.atomic
def recover(request):
    """
    Password recovery request page.
    Rate limited to 5 attempts per minute.
    """
    if request.method == "POST":
        email = request.POST.get("email", "")

        if not email.strip():
            messages.error(request, "Please enter your email.")
            return redirect(request.META.get("HTTP_REFERER", reverse("blog:index")))

        try:
            user = get_object_or_404(User, email=email)

            # Generate token
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse("auth:account_recover_confirm")
                + f"?user={user.id}&token={token}"
            )
            # Send email with reset link
            EmailService.send_password_reset_email(user.email, reset_link=reset_url)
            messages.success(
                request, "Password reset link has been sent to your email."
            )
            return redirect(
                reverse(
                    "dashboard:security_settings"
                    if request.user.is_authenticated
                    else "auth:login"
                )
            )
        except Http404:
            messages.error(request, "There is no user associated with this email.")
        except Exception as error:
            messages.error(request, f"{error}")

        return redirect(request.META.get("HTTP_REFERER", "blog:index"))

    return render(
        request,
        "auth_app/recover.html",
        {"is_authenticated": True if request.user.is_authenticated else False},
    )


@custom_ratelimit(key="ip", rate="2/h", method=["POST"])
@require_http_methods(["GET", "POST"])
@transaction.atomic
def recover_confirm(request):
    """
    Confirm password recovery page.
    Rate limited to 5 attempts per minute.
    """
    user_id = request.GET.get("user", "")
    token = request.GET.get("token", "")

    if not user_id or not token:
        messages.error(request, "Invalid or expired password recovery link.")
        return redirect(
            reverse(
                "dashboard:security_settings"
                if request.user.is_authenticated
                else "auth:login"
            )
            or reverse("blog:index")
        )

    try:
        user = get_object_or_404(User, id=user_id)
    except Exception:
        messages.error(request, "Invalid or expired password recovery link.")
        return redirect(
            reverse(
                "dashboard:security_settings"
                if request.user.is_authenticated
                else "auth:login"
            )
            or reverse("blog:index")
        )

    token_generator = PasswordResetTokenGenerator()

    if not token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired password recovery link.")
        return redirect(reverse("blog:index"))

    if request.method == "POST":
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not password.strip() or not password2.strip():
            messages.error(request, "Fill the fields properly.")
            return redirect(request.get_full_path() or reverse("blog:index"))

        if password != password2:
            messages.error(request, "Password didn't match.")
            return redirect(request.get_full_path() or reverse("blog:index"))

        try:
            validate_password(password, user)
            user.set_password(password)
            user.save()
            if request.user.is_authenticated:
                logout(request)
            messages.success(
                request,
                "Password changed successfully. Please login with your new password.",
            )
            return redirect(reverse("auth:login") or reverse("blog:index"))
        except Exception as error:
            for message in error.messages:
                messages.error(request, f"{message}")
            return redirect(request.get_full_path() or reverse("blog:index"))

    context = {"user": user}
    return render(request, "auth_app/recover_confirm.html", context)
