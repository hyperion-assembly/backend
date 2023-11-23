from django.urls import path

from callbacks.views import (
    github_callback
)

app_name = "users"
urlpatterns = [
    path("github", view=github_callback, name="github_callback"),
]
