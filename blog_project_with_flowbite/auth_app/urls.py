from django.urls import path

from . import views

app_name = "auth"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # --- Pass settings
    path("change_pass/", views.change_pass, name="change_pass"),
    path("recover/", views.recover, name="account_recover"),
    path("recover-confirm/", views.recover_confirm, name="account_recover_confirm"),
    # --- Delete
    path("delete/", views.delete_account, name="delete"),
]
