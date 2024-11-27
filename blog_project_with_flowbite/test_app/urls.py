from django.urls import include, path
from test_app.views import *

app_name="test"

urlpatterns = [
    path("", index, name="index"),
]
