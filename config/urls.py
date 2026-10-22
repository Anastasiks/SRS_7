
from django.contrib import admin
from django.urls import path, include
from dashboard.views import import_dashboard_data_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "tools/import-dashboard-data/",
        import_dashboard_data_view,
        name="import_dashboard_data",
    ),
    path("", include("dashboard.urls")),
    path("api-auth/", include("rest_framework.urls")),
]
