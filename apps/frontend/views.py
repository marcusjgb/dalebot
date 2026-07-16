from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from apps.accounts.services import create_user as create_user_account
from apps.appointments.models import Appointment, AppointmentStatus
from apps.appointments.services import (
    cancel_appointment,
    confirm_appointment,
    create_appointment,
    update_appointment,
)
from apps.businesses.services import update_business
from apps.customers.models import Customer
from apps.customers.services import create_customer
from apps.services.models import Service
from apps.services.services import create_service
from apps.staff.models import Staff
from apps.staff.services import create_staff
from apps.subscriptions.models import Subscription

User = get_user_model()


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
        status = request.GET.get("status", "")

        appointments = Appointment.objects.filter(business=business)

        if status:
            appointments = appointments.filter(status=status)

        appointments = appointments.select_related(
            "customer", "service", "staff"
        ).order_by("-starts_at")[:50]

        if request.headers.get("HX-Request"):
            return render(
                request,
                "partials/appointments_table.html",
                {"appointments": appointments},
            )

        return render(
            request,
            "pages/appointments_list.html",
            {"appointments": appointments, "current_status": status},
        )



class AppointmentCreateView(LoginRequiredMixin, View):
    def get(self, request):
        business = request.user.business
        if not business:
            return HttpResponse(
                "<div class='p-6 text-center'>"
                "<p class='text-red-600'>Error: Tu usuario no tiene un negocio asignado.</p>"
                "<p class='text-gray-600 mt-2'>Contacta al administrador.</p>"
                "</div>"
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
                "<script>"
                "document.getElementById('modal').remove();"
                "document.getElementById('modal-backdrop').remove();"
                "window.location.reload();"
                "</script>"
            )
        except Exception as e:
            error_msg = str(e)
            if "Slot not available" in error_msg:
                user_msg = (
                    "El personal no tiene disponibilidad en ese horario. "
                    "Por favor elegí otro horario o fecha."
                )
            elif "already has an appointment" in error_msg:
                user_msg = (
                    "El personal ya tiene un turno en ese horario. "
                    "Por favor elegí otro horario."
                )
            elif "not assigned to service" in error_msg:
                user_msg = "El personal seleccionado no está asignado a este servicio."
            else:
                user_msg = f"No se pudo crear el turno. {error_msg}"
            return HttpResponse(
                f"<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                f"{user_msg}"
                f"</div>"
            )


class AppointmentCancelView(LoginRequiredMixin, View):
    def post(self, request, appointment_id):
        business = request.user.business
        try:
            appointment = Appointment.objects.get(id=appointment_id, business=business)
            cancel_appointment(appointment, request.user)
            return HttpResponse("OK")
        except Exception as e:
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                f"Error al cancelar: {e}"
                "</div>"
            )


class AppointmentDetailView(LoginRequiredMixin, View):
    def get(self, request, appointment_id):
        business = request.user.business
        try:
            appointment = Appointment.objects.select_related(
                "customer", "service", "staff", "staff__user"
            ).get(id=appointment_id, business=business)
            return render(
                request,
                "partials/appointment_detail.html",
                {"appointment": appointment},
            )
        except Appointment.DoesNotExist:
            return HttpResponse(
                "<div class='p-6 text-center text-red-600'>Turno no encontrado.</div>"
            )


class AppointmentConfirmView(LoginRequiredMixin, View):
    def post(self, request, appointment_id):
        business = request.user.business
        try:
            appointment = Appointment.objects.get(id=appointment_id, business=business)
            confirm_appointment(appointment)
            return HttpResponse("OK")
        except Exception as e:
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                f"Error al confirmar: {e}"
                "</div>"
            )


class AppointmentUpdateView(LoginRequiredMixin, View):
    def get(self, request, appointment_id):
        business = request.user.business
        try:
            appointment = Appointment.objects.select_related(
                "customer", "service", "staff", "staff__user"
            ).get(id=appointment_id, business=business)
            customers = Customer.objects.filter(business=business, is_active=True)
            services = Service.objects.filter(business=business, is_active=True)
            staff_members = Staff.objects.filter(business=business, is_active=True)
            return render(
                request,
                "partials/appointment_edit_form.html",
                {
                    "appointment": appointment,
                    "customers": customers,
                    "services": services,
                    "staff_members": staff_members,
                },
            )
        except Appointment.DoesNotExist:
            return HttpResponse(
                "<div class='p-6 text-center text-red-600'>Turno no encontrado.</div>"
            )

    def post(self, request, appointment_id):
        business = request.user.business
        try:
            appointment = Appointment.objects.get(id=appointment_id, business=business)
            customer_id = request.POST.get("customer_id")
            service_id = request.POST.get("service_id")
            staff_id = request.POST.get("staff_id")
            date = request.POST.get("date")
            time = request.POST.get("time")
            notes = request.POST.get("notes", "")

            from datetime import datetime
            starts_at = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            starts_at = timezone.make_aware(starts_at)

            customer = Customer.objects.get(id=customer_id)
            service = Service.objects.get(id=service_id)
            staff = Staff.objects.get(id=staff_id)

            update_appointment(
                appointment,
                user=request.user,
                customer=customer,
                service=service,
                staff=staff,
                starts_at=starts_at,
                notes=notes,
            )
            return HttpResponse("OK")
        except Exception as e:
            error_msg = str(e)
            if "Slot not available" in error_msg:
                user_msg = (
                    "El personal no tiene disponibilidad en ese horario. "
                    "Por favor elegí otro horario o fecha."
                )
            elif "already has an appointment" in error_msg:
                user_msg = (
                    "El personal ya tiene un turno en ese horario. "
                    "Por favor elegí otro horario."
                )
            elif "not assigned to service" in error_msg:
                user_msg = "El personal seleccionado no está asignado a este servicio."
            elif "Cannot update" in error_msg:
                user_msg = f"No se puede actualizar el turno. {error_msg}"
            else:
                user_msg = f"No se pudo actualizar el turno. {error_msg}"
            return HttpResponse(
                f"<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                f"{user_msg}"
                f"</div>"
            )


class CustomersListView(LoginRequiredMixin, View):
    def get(self, request):
        business = request.user.business
        if not business:
            return HttpResponse(
                "<div class='p-6 text-center'>"
                "<p class='text-red-600'>Error: No tenés un negocio asignado.</p>"
                "</div>"
            )
        customers = Customer.objects.filter(business=business).prefetch_related("appointments")
        return render(request, "pages/customers_list.html", {"customers": customers})


class CustomerCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "partials/customer_form.html")

    def post(self, request):
        business = request.user.business
        if not business:
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                "Error: No tenés un negocio asignado."
                "</div>"
            )

        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email", "")
        notes = request.POST.get("notes", "")

        try:
            create_customer(
                business=business,
                name=name,
                phone=phone,
                email=email,
                notes=notes,
            )
            return HttpResponse(
                "<script>"
                "document.getElementById('modal').remove();"
                "document.getElementById('modal-backdrop').remove();"
                "window.location.reload();"
                "</script>"
            )
        except Exception as e:
            error_msg = str(e)
            if "unique" in error_msg.lower():
                user_msg = "Ya existe un cliente con ese número de teléfono."
            else:
                user_msg = f"No se pudo crear el cliente. {error_msg}"
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                f"{user_msg}"
                "</div>"
            )


class ServicesListView(LoginRequiredMixin, View):
    def get(self, request):
        business = request.user.business
        if not business:
            return HttpResponse(
                "<div class='p-6 text-center'>"
                "<p class='text-red-600'>Error: No tenés un negocio asignado.</p>"
                "</div>"
            )
        services = Service.objects.filter(business=business)
        return render(request, "pages/services_list.html", {"services": services})


class ServiceCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "partials/service_form.html")

    def post(self, request):
        business = request.user.business
        if not business:
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                "Error: No tenés un negocio asignado."
                "</div>"
            )

        name = request.POST.get("name")
        description = request.POST.get("description", "")
        duration = request.POST.get("duration_minutes", "30")
        price = request.POST.get("price", "0")

        try:
            create_service(
                business=business,
                name=name,
                duration_minutes=int(duration),
                price=float(price) if price else 0,
                description=description,
            )
            return HttpResponse(
                "<script>"
                "document.getElementById('modal').remove();"
                "document.getElementById('modal-backdrop').remove();"
                "window.location.reload();"
                "</script>"
            )
        except Exception as e:
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                f"No se pudo crear el servicio. {e}"
                "</div>"
            )


class StaffListView(LoginRequiredMixin, View):
    def get(self, request):
        business = request.user.business
        if not business:
            return HttpResponse(
                "<div class='p-6 text-center'>"
                "<p class='text-red-600'>Error: No tenés un negocio asignado.</p>"
                "</div>"
            )
        staff_members = Staff.objects.filter(business=business).prefetch_related(
            "services", "user", "appointments"
        )
        return render(request, "pages/staff_list.html", {"staff_members": staff_members})


class StaffCreateView(LoginRequiredMixin, View):
    def get(self, request):
        business = request.user.business
        if not business:
            return HttpResponse(
                "<div class='p-6 text-center'>"
                "<p class='text-red-600'>Error: No tenés un negocio asignado.</p>"
                "</div>"
            )

        services = Service.objects.filter(business=business, is_active=True)

        existing_staff_user_ids = Staff.objects.filter(
            business=business
        ).values_list("user_id", flat=True)

        available_users = User.objects.filter(
            business=business,
            is_active=True,
        ).exclude(id__in=existing_staff_user_ids)

        return render(
            request,
            "partials/staff_create_form.html",
            {
                "available_users": available_users,
                "services": services,
            },
        )

    def post(self, request):
        business = request.user.business
        if not business:
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                "Error: No tenés un negocio asignado."
                "</div>"
            )

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        service_ids = request.POST.getlist("service_ids")

        if username and email and password:
            try:
                user = create_user_account(
                    business=business,
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role="staff",
                )
                create_staff(
                    business=business,
                    user=user,
                    service_ids=service_ids if service_ids else None,
                )
                return HttpResponse(
                    "<script>"
                    "document.getElementById('modal').remove();"
                    "document.getElementById('modal-backdrop').remove();"
                    "window.location.reload();"
                    "</script>"
                )
            except Exception as e:
                error_msg = str(e)
                if "username" in error_msg.lower():
                    user_msg = "El nombre de usuario ya existe."
                elif "email" in error_msg.lower():
                    user_msg = "El email ya está registrado."
                else:
                    user_msg = (
                        f"No se pudo crear el personal. {error_msg}"
                    )
                return HttpResponse(
                    "<div class='bg-red-50 border border-red-200 rounded-md "
                    "p-3 text-sm text-red-700'>"
                    f"{user_msg}"
                    "</div>"
                )

        user_id = request.POST.get("user_id")
        if not user_id:
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                "Error: Debés seleccionar un usuario o crear uno nuevo."
                "</div>"
            )

        try:
            user = User.objects.get(id=user_id)
            create_staff(
                business=business,
                user=user,
                service_ids=service_ids if service_ids else None,
            )
            return HttpResponse(
                "<script>"
                "document.getElementById('modal').remove();"
                "document.getElementById('modal-backdrop').remove();"
                "window.location.reload();"
                "</script>"
            )
        except Exception as e:
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                f"No se pudo crear el personal. {e}"
                "</div>"
            )


class BusinessSettingsView(LoginRequiredMixin, View):
    def get(self, request):
        business = request.user.business
        if not business:
            return redirect("dashboard")

        return render(request, "pages/business_settings.html", {"business": business})

    def post(self, request):
        business = request.user.business
        if not business:
            return redirect("dashboard")

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()
        timezone_val = request.POST.get("timezone", "America/Argentina/Buenos_Aires").strip()

        if not name:
            return HttpResponse(
                "<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                "El nombre del negocio es obligatorio."
                "</div>"
            )

        try:
            update_business(
                business,
                name=name,
                phone=phone,
                email=email,
                address=address,
                timezone=timezone_val,
            )
            return HttpResponse(
                "<div class='bg-green-50 border border-green-200 rounded-md "
                "p-3 text-sm text-green-700'>"
                "Configuración guardada correctamente."
                "</div>"
            )
        except Exception as e:
            return HttpResponse(
                f"<div class='bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700'>"
                f"Error al guardar: {e}"
                f"</div>"
            )
