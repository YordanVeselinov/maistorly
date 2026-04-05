from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from jobs.models import JobRequest, Offer


class Review(models.Model):
    job_request = models.ForeignKey(
        JobRequest,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )
    craftsman = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("reviewer", "job_request", "craftsman"),
                name="reviews_unique_reviewer_job_request_craftsman",
            ),
        ]

    def __str__(self) -> str:
        return f"Review for {self.craftsman} on {self.job_request.title}"

    def clean(self):
        errors = {}

        if self.job_request_id and self.reviewer_id and self.job_request.owner_id != self.reviewer_id:
            errors["reviewer"] = "Only the job owner can create a review for this job request."

        if self.job_request_id and self.job_request.status != JobRequest.Status.COMPLETED:
            errors["job_request"] = "A review can only be created for a completed job request."

        if self.craftsman_id and self.job_request_id and self.craftsman_id == self.job_request.owner_id:
            errors["craftsman"] = "The job owner cannot review themselves as the craftsman."

        if (
            self.craftsman_id
            and self.job_request_id
            and not Offer.objects.filter(
                job_request_id=self.job_request_id,
                craftsman_id=self.craftsman_id,
            ).exists()
        ):
            errors["craftsman"] = "You can only review a craftsman who has submitted an offer for this job request."

        if (
            self.reviewer_id
            and self.job_request_id
            and self.craftsman_id
            and Review.objects.exclude(pk=self.pk).filter(
                reviewer_id=self.reviewer_id,
                job_request_id=self.job_request_id,
                craftsman_id=self.craftsman_id,
            ).exists()
        ):
            errors["craftsman"] = "You have already reviewed this craftsman for the selected job request."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
