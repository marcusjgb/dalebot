from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from apps.appointments.models import Appointment, AppointmentStatus
from apps.appointments.services import cancel_appointment, create_appointment
from apps.customers.models import Customer
from apps.services.models import Service
from apps.staff.models import Staff
from apps.subscriptions.models import Subscription


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(request, "pages/login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        return render(request, "pages/login.html", {"form": {"errors": True}})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("login")


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        business = user.business

        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        appointments_today = Appointment.objects.filter(
            business=business,
            starts_at__date=today,
        ).count()

        appointments_week = Appointment.objects.filter(
            business=business,
            starts_at__date__gte=week_start,
            starts_at__date__lte=today,
        ).count()

        customers_count = Customer.objects.filter(business=business).count()

        pending = Appointment.objects.filter(
            business=business,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED],
        ).count()

        subscription = None
        appointments_month = 0

        try:
            subscription = Subscription.objects.get(business=business)
            appointments_month = Appointment.objects.filter(
                business=business,
                created_at__date__gte=month_start,
            ).count()
        except Subscription.DoesNotExist:
            pass

        services_count = Service.objects.filter(business=business, is_active=True).count()
        staff_count = Staff.objects.filter(business=business, is_active=True).count()

        context = {
            "stats": {
                "appointments_today": appointments_today,
                "appointments_week": appointments_week,
                "customers": customers_count,
                "pending": pending,
            },
            "subscription": subscription,
            "staff_count": staff_count,
            "services_count": services_count,
            "customers_count": customers_count,
            "appointments_month": appointments_month,
        }
        return render(request, "pages/dashboard.html", context)


class UpcomingAppointmentsView(LoginRequiredMixin, View):
    def get(self, request):
        business = request.user.business
        upcoming = Appointment.objects.filter(
            business=business,
            starts_at__gte=timezone.now(),
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED],
        ).select_related("customer", "service", "staff").order_by("starts_at")[:5]

        if not upcoming:
            return HttpResponse(
                "<p class='text-gray-500 text-center'>No hay turnos próximos</p>"
            )

        html = "<div class='space-y-3'>"
        for apt in upcoming:
            staff_name = apt.staff.user.get_full_name() or apt.staff.user.username
            html += f"""
            <div class='flex justify-between items-center p-3 bg-gray-50 rounded-lg'>
                <div>
                    <div class='font-medium text-gray-900'>{apt.customer.name}</div>
                    <div class='text-sm text-gray-500'>
                        {apt.service.name} con {staff_name}
                    </div>
                </div>
                <div class='text-right'>
                    <div class='text-sm font-medium text-indigo-600'>
                        {apt.starts_at.strftime('%d/%m %H:%M')}
                    </div>
                    <div class='text-xs text-gray-500'>{apt.get_status_display()}</div>
                </div>
            </div>
            """
        html += "</div>"
        return HttpResponse(html)


class AppointmentsListView(LoginRequiredMixin, View):
    def get(self, request):
        business = request.user.business
        appointments = Appointment.objects.filter(
            business=business
        ).select_related("customer", "service", "staff").order_by("-starts_at")[:50]
        return render(request, "pages/appointments_list.html", {"appointments": appointments})


class AppointmentCreateView(LoginRequiredMixin, View):
    def get(self, request):
        business = request.user.business
        if not business:
            return HttpResponse(
                "<div class='p-6 text-center'><p class='text-red-600'>Error: Tu usuario no tiene un negocio asignado.</p><p class='text-gray-600 mt-2'>Contacta al administrador.</p></div>"
            )
        customers = Customer.objects.filter(business=business, is_active=True)
        services = Service.objects.filter(business=business, is_active=True)
        staff_members = Staff.objects.filter(business=business, is_active=True)
        return render(
            request,
            "partials/appointment_form.html",
            {
                "customers": customers,
                "services": services,
                "staff_members": staff_members,
            },
        )

    def post(self, request):
        business = request.user.business
        customer_id = request.POST.get("customer_id")
        service_id = request.POST.get("service_id")
        staff_id = request.POST.get("staff_id")
        date = request.POST.get("date")
        time = request.POST.get("time")

        from datetime import datetime
        starts_at = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        starts_at = timezone.make_aware(starts_at)

        customer = Customer.objects.get(id=customer_id)
        service = Service.objects.get(id=service_id)
        staff = Staff.objects.get(id=staff_id)

        try:
            create_appointment(
                business=business,
                customer=customer,
                service=service,
                staff=staff,
                starts_at=starts_at,
            )
            return HttpResponse(
                "<script>window.location.reload()</script>"
            )
        except Exception as e:
            return HttpResponse(f"<div class='text-red-600'>Error: {e}</div>")


class AppointmentCancelView(LoginRequiredMixin, View):
    def post(self, request, appointment_id):
        business = request.user.business
        try:
            appointment = Appointment.objects.get(id=appointment_id, business=business)
            cancel_appointment(appointment, request.user)
            appointments = Appointment.objects.filter(
                business=business
            ).select_related("customer", "service", "staff").order_by("-starts_at")[:50]
            return render(
                request,
                "partials/appointments_table.html",
                {"appointments": appointments},
            )
        except Exception as e:
            return HttpResponse(f"<div class='text-red-600'>Error: {e}</div>")
