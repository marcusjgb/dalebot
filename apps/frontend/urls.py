from django.urls import path

from .views import (
    AppointmentCancelView,
    AppointmentCreateView,
    AppointmentsListView,
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
        name="upcoming_appointments",
    ),
    path(
        "appointments/",
        AppointmentsListView.as_view(),
        name="appointments_list",
    ),
    path(
        "appointments/create/",
        AppointmentCreateView.as_view(),
        name="appointments_create",
    ),
    path(
        "appointments/<uuid:appointment_id>/cancel/",
        AppointmentCancelView.as_view(),
        name="appointments_cancel",
    ),
]
