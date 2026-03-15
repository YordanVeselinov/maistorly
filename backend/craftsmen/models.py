from django.conf import settings
from django.db import models

from services.models import Skill


class CraftsmanProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="craftsman_profile",
    )
    skills = models.ManyToManyField(
        Skill,
        related_name="craftsmen",
        blank=True,
    )
    display_name = models.CharField(
        max_length=120,
        blank=True,
    )
    bio = models.TextField(blank=True)
    phone = models.CharField(
        max_length=32,
        blank=True,
    )
    city = models.CharField(
        max_length=100,
        blank=True,
    )
    country = models.CharField(
        max_length=100,
        blank=True,
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("user__username",)

    def __str__(self) -> str:
        return self.display_name or self.user.get_username()
