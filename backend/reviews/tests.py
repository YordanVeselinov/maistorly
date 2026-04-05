from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.signals import CRAFTSMEN_GROUP
from accounts.models import User
from craftsmen.models import CraftsmanProfile
from jobs.models import JobRequest, Offer

from .models import Review


class ReviewModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="reviewowner",
            email="reviewowner@example.com",
            password="StrongPass12345!",
        )
        self.craftsman = User.objects.create_user(
            username="reviewcraftsman",
            email="reviewcraftsman@example.com",
            password="StrongPass12345!",
        )
        craftsmen_group, _ = Group.objects.get_or_create(name=CRAFTSMEN_GROUP)
        self.craftsman.groups.add(craftsmen_group)
        self.job_request = JobRequest.objects.create(
            owner=self.owner,
            title="Repair wall crack",
            description="Bedroom wall has a large crack.",
            city="Sofia",
            budget_min="100.00",
            budget_max="200.00",
            preferred_date=timezone.localdate() + timedelta(days=2),
            status=JobRequest.Status.OPEN,
        )
        Offer.objects.create(
            job_request=self.job_request,
            craftsman=self.craftsman,
            message="I can repair and repaint the wall.",
            proposed_price="180.00",
            estimated_days=2,
        )

    def test_review_can_only_be_created_for_completed_job(self):
        review = Review(
            job_request=self.job_request,
            reviewer=self.owner,
            craftsman=self.craftsman,
            rating=5,
            comment="Great work.",
        )

        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_only_one_review_per_reviewer_job_and_craftsman_is_allowed(self):
        self.job_request.status = JobRequest.Status.COMPLETED
        self.job_request.save()
        Review.objects.create(
            job_request=self.job_request,
            reviewer=self.owner,
            craftsman=self.craftsman,
            rating=5,
            comment="Great work.",
        )

        duplicate_review = Review(
            job_request=self.job_request,
            reviewer=self.owner,
            craftsman=self.craftsman,
            rating=4,
            comment="Second review.",
        )

        with self.assertRaises(ValidationError):
            duplicate_review.full_clean()


class ReviewViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="reviewowner2",
            email="reviewowner2@example.com",
            password="StrongPass12345!",
        )
        self.other_user = User.objects.create_user(
            username="otherreviewer",
            email="otherreviewer@example.com",
            password="StrongPass12345!",
        )
        self.craftsman = User.objects.create_user(
            username="reviewcraftsman2",
            email="reviewcraftsman2@example.com",
            password="StrongPass12345!",
        )
        craftsmen_group, _ = Group.objects.get_or_create(name=CRAFTSMEN_GROUP)
        self.craftsman.groups.add(craftsmen_group)
        self.craftsman_profile = CraftsmanProfile.objects.create(user=self.craftsman, display_name="Painter Pro")
        self.job_request = JobRequest.objects.create(
            owner=self.owner,
            title="Paint hallway",
            description="Need hallway painted.",
            city="Plovdiv",
            budget_min="120.00",
            budget_max="220.00",
            preferred_date=timezone.localdate() + timedelta(days=3),
            status=JobRequest.Status.COMPLETED,
        )
        Offer.objects.create(
            job_request=self.job_request,
            craftsman=self.craftsman,
            message="I can finish it over the weekend.",
            proposed_price="210.00",
            estimated_days=2,
        )

    def test_job_owner_can_create_review_for_completed_job(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse(
                "reviews:review_create",
                kwargs={"job_pk": self.job_request.pk, "craftsman_pk": self.craftsman_profile.pk},
            ),
            data={
                "rating": 5,
                "comment": "Excellent work and communication.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Review.objects.filter(
                job_request=self.job_request,
                reviewer=self.owner,
                craftsman=self.craftsman,
            ).exists()
        )

    def test_non_owner_cannot_create_review(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                "reviews:review_create",
                kwargs={"job_pk": self.job_request.pk, "craftsman_pk": self.craftsman_profile.pk},
            )
        )

        self.assertEqual(response.status_code, 403)
