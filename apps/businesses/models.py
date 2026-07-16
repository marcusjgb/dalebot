import uuid

from django.db import models


class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    timezone = models.CharField(max_length=50, default="America/Argentina/Buenos_Aires")
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    address = models.TextField(blank=True, default="")
    logo_url = models.URLField(blank=True, default="")
    whatsapp_phone_number_id = models.CharField(max_length=50, blank=True, default="")
    whatsapp_verify_token = models.CharField(max_length=100, blank=True, default="")
    whatsapp_access_token = models.CharField(max_length=255, blank=True, default="")
    whatsapp_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "businesses"

    def __str__(self):
        return self.name
