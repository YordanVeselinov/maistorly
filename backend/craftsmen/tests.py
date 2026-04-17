from unittest.mock import patch

from cloudinary import CloudinaryResource
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.signals import CLIENTS_GROUP, CRAFTSMEN_GROUP
from accounts.models import User
from services.models import Category, Skill

from .models import CraftsmanProfile, ServiceListing


class CraftsmanProfileModelTests(TestCase):
    def test_profile_can_have_multiple_skills(self):
        user = User.objects.create_user(
            username="craftsman1",
            email="craftsman1@example.com",
            password="StrongPass12345!",
        )
        category = Category.objects.create(name="Plumbing")
        skill_one = Skill.objects.create(category=category, name="Pipe Repair")
        skill_two = Skill.objects.create(category=category, name="Leak Detection")

        profile = CraftsmanProfile.objects.create(user=user, display_name="Master Plumber")
        profile.skills.set([skill_one, skill_two])

        self.assertEqual(profile.skills.count(), 2)
        self.assertQuerySetEqual(
            profile.skills.order_by("name"),
            Skill.objects.filter(pk__in=[skill_two.pk, skill_one.pk]).order_by("name"),
        )

    def test_string_representation_falls_back_to_username(self):
        user = User.objects.create_user(
            username="craftsman2",
            email="craftsman2@example.com",
            password="StrongPass12345!",
        )

        profile = CraftsmanProfile.objects.create(user=user)

        self.assertEqual(str(profile), "craftsman2")


class ServiceListingViewTests(TestCase):
    def setUp(self):
        self.clients_group, _ = Group.objects.get_or_create(name=CLIENTS_GROUP)
        self.craftsmen_group, _ = Group.objects.get_or_create(name=CRAFTSMEN_GROUP)
        self.craftsman = User.objects.create_user(
            username="listingcraftsman",
            email="listingcraftsman@example.com",
            password="StrongPass12345!",
        )
        self.client_user = User.objects.create_user(
            username="listingclient",
            email="listingclient@example.com",
            password="StrongPass12345!",
        )
        self.craftsman.groups.add(self.craftsmen_group)
        self.client_user.groups.add(self.clients_group)

        self.category = Category.objects.create(name="Plastering")
        self.skill = Skill.objects.create(category=self.category, name="Wall Repair")
        self.listing = ServiceListing.objects.create(
            craftsman=self.craftsman,
            title="Tile replacement",
            description="Replace broken tiles and refresh grout.",
            rough_price="200.00",
            category=self.category,
        )

    @patch("cloudinary.uploader.upload_resource")
    def test_craftsman_can_create_service_listing(self, mocked_upload):
        mocked_upload.return_value = CloudinaryResource(
            "service_listings/images/work-sample",
            resource_type="image",
            type="upload",
        )
        self.client.force_login(self.craftsman)
        image = SimpleUploadedFile(
            "work-sample.jpg",
            b"fake-image-content",
            content_type="image/jpeg",
        )

        response = self.client.post(
            reverse("craftsmen:service_listing_create"),
            data={
                "title": "Wall crack repair",
                "description": "Repair and smooth cracked interior walls.",
                "rough_price": "150.00",
                "category": self.category.pk,
                "skills": [self.skill.pk],
                "images": [image],
            },
        )

        self.assertEqual(response.status_code, 302)
        listing = ServiceListing.objects.get(title="Wall crack repair")
        self.assertEqual(listing.craftsman, self.craftsman)
        self.assertEqual(listing.images.count(), 1)
        mocked_upload.assert_called_once()

    def test_client_cannot_create_service_listing(self):
        self.client.force_login(self.client_user)

        response = self.client.post(
            reverse("craftsmen:service_listing_create"),
            data={
                "title": "Should be blocked",
                "description": "Blocked for clients.",
                "rough_price": "100.00",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(ServiceListing.objects.filter(title="Should be blocked").exists())

    def test_anonymous_user_can_access_service_listing_marketplace(self):
        response = self.client.get(reverse("craftsmen:service_listing_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tile replacement")

    def test_non_craftsman_user_can_access_service_listing_detail(self):
        self.client.force_login(self.client_user)

        response = self.client.get(
            reverse("craftsmen:service_listing_detail", kwargs={"pk": self.listing.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tile replacement")

    def test_craftsman_cannot_access_public_service_listing_marketplace(self):
        self.client.force_login(self.craftsman)

        response = self.client.get(reverse("craftsmen:service_listing_list"))

        self.assertEqual(response.status_code, 403)

    def test_craftsman_cannot_access_public_service_listing_detail(self):
        self.client.force_login(self.craftsman)

        response = self.client.get(
            reverse("craftsmen:service_listing_detail", kwargs={"pk": self.listing.pk})
        )

        self.assertEqual(response.status_code, 403)
