import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class UserRole(models.TextChoices):
    OWNER = "owner", "Propietario"
    ADMIN = "admin", "Administrador"
    STAFF = "staff", "Personal"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STAFF,
    )

    objects = UserManager()

    class Meta:
        db_table = "accounts_user"

    @property
    def is_owner(self):
        return self.role == UserRole.OWNER

    @property
    def is_admin(self):
        return self.role in [UserRole.OWNER, UserRole.ADMIN]

    @property
    def can_manage_business(self):
        return self.role in [UserRole.OWNER, UserRole.ADMIN]
