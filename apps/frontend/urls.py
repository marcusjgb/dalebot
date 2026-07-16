from django.urls import path

from .views import (
    DashboardView,
    LoginView,
    LogoutView,
    UpcomingAppointmentsView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path(
        "appointments/upcoming/",
        UpcomingAppointmentsView.as_view(),
        name="appointments:upcoming",
    ),
]
