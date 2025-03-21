# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path(
        "",
        login_required(TemplateView.as_view(template_name="index-admin.html")),
        name="home",
    ),
    path(
        "dashboard/",
        login_required(TemplateView.as_view(template_name="dashboard/dash.html")),
        name="dash",
    ),
    path(
        "elements/bc_color",
        login_required(TemplateView.as_view(template_name="elements/bc_color.html")),
        name="bc_color",
    ),
    path(
        "elements/bc_typography",
        login_required(
            TemplateView.as_view(template_name="elements/bc_typography.html")
        ),
        name="bc_typography",
    ),
    path(
        "elements/icon_tabler",
        login_required(TemplateView.as_view(template_name="elements/icon-tabler.html")),
        name="icon-tabler",
    ),
    path(
        "elements/bc_modal",
        login_required(TemplateView.as_view(template_name="elements/bc_modal.html")),
        name="bc_modal",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("buzztialab.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("wallet/", include("buzztialab.apps.wallet.urls", namespace="wallet")),
    path(
        "residential_units/",
        include(
            "buzztialab.apps.residential_units.urls", namespace="residential_units"
        ),
    ),
    path("whatsapp/", include("buzztialab.apps.whatsapp.urls", namespace="whatsapp")),
    # Your stuff: custom urls includes go here
    # ...
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("api/auth-token/", obtain_auth_token),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
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
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
