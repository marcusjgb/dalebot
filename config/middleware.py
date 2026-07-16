from django.utils import timezone


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.business = None

        if hasattr(request, "user") and request.user.is_authenticated:
            request.business = getattr(request.user, "business", None)

        return self.get_response(request)


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.audit_data = {
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
        }
        return self.get_response(request)

    def _get_client_ip(self, request):
        x_forwarded = request.headers.get("X-Forwarded-For")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
