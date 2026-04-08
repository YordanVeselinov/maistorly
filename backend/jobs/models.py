from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from services.models import Category, Skill


class JobRequest(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_requests",
    )
    title = models.CharField(
        max_length=200,
    )
    description = models.TextField()
    city = models.CharField(
        max_length=100,
    )
    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    preferred_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    categories = models.ManyToManyField(
        Category,
        related_name="job_requests",
        blank=True,
    )
    required_skills = models.ManyToManyField(
        Skill,
        related_name="job_requests",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

    def clean(self):
        errors = {}

        if self.budget_min is not None and self.budget_min < 0:
            errors["budget_min"] = "Minimum budget cannot be negative."

        if (
            self.budget_min is not None
            and self.budget_max is not None
            and self.budget_max < self.budget_min
        ):
            errors["budget_max"] = "Maximum budget cannot be less than minimum budget."

        if self.preferred_date and self.preferred_date < timezone.localdate():
            errors["preferred_date"] = "Preferred date cannot be in the past."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class JobRequestImage(models.Model):
    job_request = models.ForeignKey(
        JobRequest,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.FileField(
        upload_to="job_requests/images/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"],
            )
        ],
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"Image for {self.job_request.title}"


class Offer(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    job_request = models.ForeignKey(
        JobRequest,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    craftsman = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_offers",
    )
    message = models.TextField()
    proposed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    estimated_days = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Offer by {self.craftsman} for {self.job_request.title}"

    def clean(self):
        if self.craftsman_id and self.job_request_id and self.craftsman_id == self.job_request.owner_id:
            raise ValidationError(
                {"craftsman": "The job owner cannot submit an offer for their own job request."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

