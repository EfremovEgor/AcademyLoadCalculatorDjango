from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from . import settings


static_urlpatterns = [
    re_path(
        r"^static/(?P<path>.*)$",
        serve,
        {"document_root": settings.STATIC_ROOT},
    ),
]
urlpatterns = [
    path("", include(static_urlpatterns)),
    path("admin/", admin.site.urls),
    path("", include("website.urls")),
]
