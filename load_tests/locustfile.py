from locust import HttpUser, task, between
import random


class BusinessUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.business_id = None
        self.staff_id = None
        self.service_id = None

    @task(3)
    def view_appointments(self):
        if self.business_id:
            self.client.get(
                f"/api/businesses/{self.business_id}/appointments/",
                name="/api/businesses/[id]/appointments/"
            )

    @task(2)
    def view_daily_schedule(self):
        if self.business_id:
            self.client.get(
                f"/api/businesses/{self.business_id}/appointments/?date=today",
                name="/api/businesses/[id]/appointments/?date=today"
            )

    @task(2)
    def view_customers(self):
        if self.business_id:
            self.client.get(
                f"/api/businesses/{self.business_id}/customers/",
                name="/api/businesses/[id]/customers/"
            )

    @task(1)
    def create_appointment(self):
        if self.business_id and self.service_id and self.staff_id:
            payload = {
                "service_id": str(self.service_id),
                "staff_id": str(self.staff_id),
                "starts_at": "2026-07-20T10:00:00Z",
            }
            self.client.post(
                f"/api/businesses/{self.business_id}/appointments/",
                json=payload,
                name="/api/businesses/[id]/appointments/"
            )

    @task(1)
    def view_services(self):
        if self.business_id:
            self.client.get(
                f"/api/businesses/{self.business_id}/services/",
                name="/api/businesses/[id]/services/"
            )


class WhatsAppWebhookUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def webhook_message(self):
        payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "123456789",
                "changes": [{
                    "value": {
                        "metadata": {"phone_number_id": "123456789"},
                        "messages": [{
                            "id": f"wamid.{random.randint(1000000, 9999999)}",
                            "from": "+5491112345678",
                            "type": "text",
                            "text": {"body": "Hola, quiero reservar"},
                        }]
                    },
                    "change": "messages"
                }]
            }]
        }
        self.client.post(
            "/api/whatsapp/webhook/",
            json=payload,
            name="/api/whatsapp/webhook/"
        )


class HealthCheckUser(HttpUser):
    wait_time = between(30, 60)

    @task
    def health_check(self):
        self.client.get("/health/")
