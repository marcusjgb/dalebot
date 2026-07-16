import hashlib
import hmac
import os
from functools import wraps

from django.http import JsonResponse


def verify_meta_signature(request):
    app_secret = os.environ.get("WHATSAPP_APP_SECRET", "")
    if not app_secret:
        return True

    headers = request.headers
    signature = headers.get("X-Hub-Signature-256", "").replace("sha256=", "")

    if not signature:
        return False

    payload = request.body
    expected = hmac.new(
        app_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)


def meta_webhook_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == os.environ.get("WHATSAPP_VERIFY_TOKEN"):
            return JsonResponse({"challenge": int(challenge)})

        if not verify_meta_signature(request):
            return JsonResponse({"error": "Invalid signature"}, status=403)

        return view_func(request, *args, **kwargs)
    return wrapper
