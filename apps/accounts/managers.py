from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserQuerySet(models.QuerySet):
    def for_business(self, business):
        return self.filter(business=business)

    def active(self):
        return self.filter(is_active=True)


class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def for_business(self, business):
        return self.get_queryset().for_business(business)

    def active(self):
        return self.get_queryset().active()
