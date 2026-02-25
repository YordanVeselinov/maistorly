from django.conf import settings
from django.db import models


class CustomerAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_account',
    )

    phone = models.CharField(
        max_length=32,
        blank=True,
    )

    address_line1 = models.CharField(
        max_length=255,
        blank=True,

    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    postal_code = models.CharField(
        max_length=32,
        blank=True,
    )

    country = models.CharField(
        max_length=100,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self) -> str:
        return f'CustomerAccount({self.user})'
