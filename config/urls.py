from django.contrib import admin
from django.urls import include, path

from .views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.accounts.urls")),
    path("api/whatsapp/", include("apps.whatsapp.urls")),
    path("health/", health, name="health"),
    path("", include("apps.frontend.urls")),
    path("", include("django_prometheus.urls")),
]
