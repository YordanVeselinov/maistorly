from cloudinary.models import CloudinaryField
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models

from services.models import Category, Skill

IMAGE_VALIDATORS = [
    FileExtensionValidator(
        allowed_extensions=["jpg", "jpeg", "png", "webp"],
    )
]


def service_listing_image_field():
    if settings.CLOUDINARY_ENABLED:
        return CloudinaryField(
            "image",
            folder="service_listings/images",
            resource_type="image",
            validators=IMAGE_VALIDATORS,
        )

    return models.FileField(
        upload_to="service_listings/images/",
        max_length=255,
        validators=IMAGE_VALIDATORS,
    )


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


class ServiceListing(models.Model):
    craftsman = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_listings",
    )
    title = models.CharField(
        max_length=200,
    )
    description = models.TextField()
    rough_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="service_listings",
        null=True,
        blank=True,
    )
    skills = models.ManyToManyField(
        Skill,
        related_name="service_listings",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title


class ServiceListingImage(models.Model):
    listing = models.ForeignKey(
        ServiceListing,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = service_listing_image_field()
    caption = models.CharField(
        max_length=200,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"Image for {self.listing.title}"
