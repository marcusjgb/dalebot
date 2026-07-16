import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .services import process_webhook_event
from .webhooks import meta_webhook_required


@method_decorator(csrf_exempt, name="dispatch")
class WhatsAppWebhookView(View):
    @method_decorator(meta_webhook_required)
    def post(self, request):
        payload = json.loads(request.body)
        result = process_webhook_event(payload)

        if result.get("status") == "duplicate":
            return JsonResponse({"status": "ok"})

        if result.get("status") == "error":
            return JsonResponse({"error": result.get("error")}, status=500)

        return JsonResponse({"status": "ok"})
