import os

import requests

WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"


def send_whatsapp_message(business, to_phone, content):
    phone_number_id = _get_phone_number_id(business)
    if not phone_number_id:
        raise ValueError(f"No WhatsApp account configured for business {business.id}")

    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")

    url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": content},
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def send_template_message(business, to_phone, template_name, components=None):
    phone_number_id = _get_phone_number_id(business)
    if not phone_number_id:
        raise ValueError(f"No WhatsApp account configured for business {business.id}")

    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")

    url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "es_AR"},
            "components": components or [],
        },
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def _get_phone_number_id(business):
    try:
        account = business.whatsapp_account
        return account.phone_number_id
    except Exception:
        return None
