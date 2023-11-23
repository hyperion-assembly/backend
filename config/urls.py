from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from hyperion_backend.admin import admin_site

# from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from dj_rest_auth.registration.views import SocialLoginView
# from dj_rest_auth.registration.views import SocialConnectView


# class GitHubLogin(SocialLoginView):
#     adapter_class = GitHubOAuth2Adapter
#     callback_url = "http://localhost:8000/accounts/github/login/callback/"
#     client_class = OAuth2Client


# class GithubConnect(SocialConnectView):
#     adapter_class = GitHubOAuth2Adapter
#     callback_url = "http://localhost:8000/accounts/github/login/callback/"
#     client_class = OAuth2Client


urlpatterns = [

    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    # path(settings.ADMIN_URL, admin.site.urls),
    path(settings.ADMIN_URL, admin_site.urls),
    # User management
    path("callbacks/", include("callbacks.urls", namespace="callbacks")),
    # path("accounts/", include("allauth.urls")),
    # path("dj-rest-auth/", include("dj_rest_auth.urls")),
    # path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    # path("dj-rest-auth/github/", GitHubLogin.as_view(), name="github_login"),
    # path("dj-rest-auth/github/connect/", GithubConnect.as_view(), name="github_connect"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # allows the error pages to be debugged during development
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
