from datetime import timedelta
from unittest.mock import patch

from cloudinary import CloudinaryResource
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.signals import CLIENTS_GROUP, CRAFTSMEN_GROUP
from accounts.models import User
from services.models import Category, Skill

from .forms import JobRequestCreateForm
from .models import JobRequest, Offer


class JobRequestFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Plumbing")
        self.skill = Skill.objects.create(category=self.category, name="Pipe Repair")

    def test_job_request_create_form_rejects_budget_max_below_budget_min(self):
        form = JobRequestCreateForm(
            data={
                "title": "Leaking pipe",
                "description": "Kitchen pipe is leaking.",
                "city": "Sofia",
                "budget_min": "200.00",
                "budget_max": "100.00",
                "preferred_date": timezone.localdate() + timedelta(days=1),
                "categories": [self.category.pk],
                "required_skills": [self.skill.pk],
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("budget_max", form.errors)

    def test_job_request_create_form_rejects_past_preferred_date(self):
        form = JobRequestCreateForm(
            data={
                "title": "Broken switch",
                "description": "Living room switch is not working.",
                "city": "Plovdiv",
                "budget_min": "50.00",
                "budget_max": "100.00",
                "preferred_date": timezone.localdate() - timedelta(days=1),
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("preferred_date", form.errors)


class JobRequestViewTests(TestCase):
    def setUp(self):
        self.clients_group, _ = Group.objects.get_or_create(name=CLIENTS_GROUP)
        self.craftsmen_group, _ = Group.objects.get_or_create(name=CRAFTSMEN_GROUP)
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass12345!",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass12345!",
        )
        self.craftsman_user = User.objects.create_user(
            username="viewer_craftsman",
            email="viewer_craftsman@example.com",
            password="StrongPass12345!",
        )
        self.owner.groups.add(self.clients_group)
        self.other_user.groups.add(self.clients_group)
        self.craftsman_user.groups.add(self.craftsmen_group)
        self.category = Category.objects.create(name="Electrical")
        self.skill = Skill.objects.create(category=self.category, name="Wiring")
        self.job_request = JobRequest.objects.create(
            owner=self.owner,
            title="Fix light",
            description="Ceiling light is broken.",
            city="Sofia",
            budget_min="80.00",
            budget_max="150.00",
            preferred_date=timezone.localdate() + timedelta(days=2),
        )
        self.job_request.categories.add(self.category)
        self.job_request.required_skills.add(self.skill)

    @patch("cloudinary.uploader.upload_resource")
    def test_authenticated_user_can_create_job_request_and_becomes_owner(self, mocked_upload):
        mocked_upload.return_value = CloudinaryResource(
            "job_requests/images/install-faucet",
            resource_type="image",
            type="upload",
        )
        self.client.force_login(self.other_user)
        image = SimpleUploadedFile(
            "reference.jpg",
            b"fake-image-content",
            content_type="image/jpeg",
        )

        response = self.client.post(
            reverse("jobs:job_create"),
            data={
                "title": "Install faucet",
                "description": "Need a new bathroom faucet installed.",
                "city": "Varna",
                "budget_min": "120.00",
                "budget_max": "200.00",
                "preferred_date": timezone.localdate() + timedelta(days=3),
                "categories": [self.category.pk],
                "required_skills": [self.skill.pk],
                "images": [image],
            },
        )

        self.assertEqual(response.status_code, 302)
        job_request = JobRequest.objects.get(title="Install faucet")
        self.assertEqual(job_request.owner, self.other_user)
        self.assertEqual(job_request.images.count(), 1)
        if settings.CLOUDINARY_ENABLED:
            mocked_upload.assert_called_once()
        else:
            mocked_upload.assert_not_called()

    def test_anonymous_user_cannot_access_job_request_list(self):
        response = self.client.get(reverse("jobs:job_list"))

        self.assertEqual(response.status_code, 403)

    def test_client_cannot_access_job_request_list(self):
        self.client.force_login(self.other_user)

        response = self.client.get(reverse("jobs:job_list"))

        self.assertEqual(response.status_code, 403)

    def test_craftsman_can_access_job_request_list(self):
        self.client.force_login(self.craftsman_user)

        response = self.client.get(reverse("jobs:job_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fix light")

    def test_owner_can_access_own_job_request_detail(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("jobs:job_detail", kwargs={"pk": self.job_request.pk}))

        self.assertEqual(response.status_code, 200)

    def test_non_owner_client_cannot_access_job_request_detail(self):
        self.client.force_login(self.other_user)

        response = self.client.get(reverse("jobs:job_detail", kwargs={"pk": self.job_request.pk}))

        self.assertEqual(response.status_code, 403)

    def test_craftsman_can_access_job_request_detail(self):
        self.client.force_login(self.craftsman_user)

        response = self.client.get(reverse("jobs:job_detail", kwargs={"pk": self.job_request.pk}))

        self.assertEqual(response.status_code, 200)

    def test_craftsman_cannot_create_job_request(self):
        craftsman = User.objects.create_user(
            username="craftsman_forbidden",
            email="craftsman_forbidden@example.com",
            password="StrongPass12345!",
        )
        craftsman.groups.add(self.craftsmen_group)
        self.client.force_login(craftsman)

        response = self.client.post(
            reverse("jobs:job_create"),
            data={
                "title": "Blocked request",
                "description": "This should not be allowed.",
                "city": "Sofia",
                "budget_min": "100.00",
                "budget_max": "150.00",
                "preferred_date": timezone.localdate() + timedelta(days=2),
                "categories": [self.category.pk],
                "required_skills": [self.skill.pk],
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(JobRequest.objects.filter(title="Blocked request").exists())

    def test_non_owner_cannot_update_job_request(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("jobs:job_update", kwargs={"pk": self.job_request.pk}),
            data={
                "title": "Updated title",
                "description": self.job_request.description,
                "city": self.job_request.city,
                "budget_min": self.job_request.budget_min,
                "budget_max": self.job_request.budget_max,
                "preferred_date": self.job_request.preferred_date,
                "status": self.job_request.status,
                "categories": [self.category.pk],
                "required_skills": [self.skill.pk],
            },
        )

        self.assertEqual(response.status_code, 404)
        self.job_request.refresh_from_db()
        self.assertEqual(self.job_request.title, "Fix light")

    def test_non_owner_cannot_delete_job_request(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("jobs:job_delete", kwargs={"pk": self.job_request.pk}),
            data={"confirm": True},
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(JobRequest.objects.filter(pk=self.job_request.pk).exists())


class OfferViewTests(TestCase):
    def setUp(self):
        self.clients_group, _ = Group.objects.get_or_create(name=CLIENTS_GROUP)
        self.owner = User.objects.create_user(
            username="owner2",
            email="owner2@example.com",
            password="StrongPass12345!",
        )
        self.craftsman = User.objects.create_user(
            username="craftsman1",
            email="craftsman1@example.com",
            password="StrongPass12345!",
        )
        self.client_user = User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="StrongPass12345!",
        )
        self.owner.groups.add(self.clients_group)
        self.client_user.groups.add(self.clients_group)
        craftsmen_group, _ = Group.objects.get_or_create(name=CRAFTSMEN_GROUP)
        self.craftsman.groups.add(craftsmen_group)

        self.job_request = JobRequest.objects.create(
            owner=self.owner,
            title="Repair outlet",
            description="Power outlet is not working.",
            city="Sofia",
            budget_min="90.00",
            budget_max="180.00",
            preferred_date=timezone.localdate() + timedelta(days=2),
        )

    @patch("jobs.views.send_offer_notification_email.delay")
    def test_craftsman_can_create_offer(self, mocked_delay):
        self.client.force_login(self.craftsman)

        response = self.client.post(
            reverse("jobs:offer_create", kwargs={"pk": self.job_request.pk}),
            data={
                "message": "I can do the repair tomorrow.",
                "proposed_price": "140.00",
                "estimated_days": 1,
            },
        )

        self.assertEqual(response.status_code, 302)
        offer = Offer.objects.get(job_request=self.job_request, craftsman=self.craftsman)
        self.assertEqual(offer.proposed_price, 140)
        mocked_delay.assert_called_once_with(offer.pk)

    @patch("jobs.views.send_offer_notification_email.delay")
    def test_craftsman_can_create_offer_without_estimated_days(self, mocked_delay):
        self.client.force_login(self.craftsman)

        response = self.client.post(
            reverse("jobs:offer_create", kwargs={"pk": self.job_request.pk}),
            data={
                "message": "I can start next week.",
                "proposed_price": "160.00",
                "estimated_days": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        offer = Offer.objects.get(job_request=self.job_request, craftsman=self.craftsman)
        self.assertIsNone(offer.estimated_days)
        mocked_delay.assert_called_once_with(offer.pk)

    def test_only_craftsmen_can_create_offers(self):
        self.client.force_login(self.client_user)

        response = self.client.get(reverse("jobs:offer_create", kwargs={"pk": self.job_request.pk}))

        self.assertEqual(response.status_code, 403)

    def test_job_owner_cannot_create_offer_even_if_in_craftsmen_group(self):
        craftsmen_group, _ = Group.objects.get_or_create(name=CRAFTSMEN_GROUP)
        self.owner.groups.add(craftsmen_group)
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("jobs:offer_create", kwargs={"pk": self.job_request.pk}),
            data={
                "message": "I want to offer on my own job.",
                "proposed_price": "100.00",
                "estimated_days": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You cannot submit an offer for your own job request.")
        self.assertFalse(Offer.objects.filter(job_request=self.job_request, craftsman=self.owner).exists())

    def test_only_job_owner_sees_received_offers_in_job_detail(self):
        Offer.objects.create(
            job_request=self.job_request,
            craftsman=self.craftsman,
            message="Counter-offer message",
            proposed_price="130.00",
            estimated_days=2,
        )

        self.client.force_login(self.owner)
        owner_response = self.client.get(reverse("jobs:job_detail", kwargs={"pk": self.job_request.pk}))
        self.assertContains(owner_response, "Received Counter-Offers")
        self.assertContains(owner_response, "Counter-offer message")

        self.client.force_login(self.craftsman)
        craftsman_response = self.client.get(reverse("jobs:job_detail", kwargs={"pk": self.job_request.pk}))
        self.assertNotContains(craftsman_response, "Received Counter-Offers")
        self.assertNotContains(craftsman_response, "Counter-offer message")

    def test_job_owner_can_access_my_received_offers_page(self):
        Offer.objects.create(
            job_request=self.job_request,
            craftsman=self.craftsman,
            message="Counter-offer message",
            proposed_price="130.00",
            estimated_days=2,
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse("jobs:my_received_offers"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Received Offers")
        self.assertContains(response, "Counter-offer message")

    def test_craftsman_cannot_access_my_received_offers_page(self):
        self.client.force_login(self.craftsman)

        response = self.client.get(reverse("jobs:my_received_offers"))

        self.assertEqual(response.status_code, 403)


class JobApiTests(TestCase):
    def setUp(self):
        self.clients_group, _ = Group.objects.get_or_create(name=CLIENTS_GROUP)
        self.craftsmen_group, _ = Group.objects.get_or_create(name=CRAFTSMEN_GROUP)
        self.owner = User.objects.create_user(
            username="apiowner",
            email="apiowner@example.com",
            password="StrongPass12345!",
        )
        self.craftsman = User.objects.create_user(
            username="apiviewcraftsman",
            email="apiviewcraftsman@example.com",
            password="StrongPass12345!",
        )
        self.other_client = User.objects.create_user(
            username="apiotherclient",
            email="apiotherclient@example.com",
            password="StrongPass12345!",
        )
        self.owner.groups.add(self.clients_group)
        self.other_client.groups.add(self.clients_group)
        self.craftsman.groups.add(self.craftsmen_group)
        self.category = Category.objects.create(name="Painting")
        self.skill = Skill.objects.create(category=self.category, name="Interior Painting")
        self.job_request = JobRequest.objects.create(
            owner=self.owner,
            title="Paint bedroom",
            description="Need one bedroom repainted.",
            city="Burgas",
            budget_min="150.00",
            budget_max="300.00",
            preferred_date=timezone.localdate() + timedelta(days=5),
        )
        self.job_request.categories.add(self.category)
        self.job_request.required_skills.add(self.skill)

    def test_jobs_list_api_requires_craftsman_role(self):
        response = self.client.get(reverse("api-job-list"))

        self.assertEqual(response.status_code, 403)

    def test_craftsman_can_list_jobs_via_api(self):
        self.client.force_login(self.craftsman)

        response = self.client.get(reverse("api-job-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["title"], "Paint bedroom")

    def test_authenticated_user_can_create_job_via_api(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("api-job-list"),
            data={
                "title": "Install shelves",
                "description": "Need wall shelves installed.",
                "city": "Sofia",
                "budget_min": "60.00",
                "budget_max": "120.00",
                "preferred_date": str(timezone.localdate() + timedelta(days=4)),
                "categories": [self.category.pk],
                "required_skills": [self.skill.pk],
                "owner": 999,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        job_request = JobRequest.objects.get(title="Install shelves")
        self.assertEqual(job_request.owner, self.owner)

    def test_craftsman_cannot_create_job_via_api(self):
        craftsman = User.objects.create_user(
            username="apicraftsman",
            email="apicraftsman@example.com",
            password="StrongPass12345!",
        )
        craftsman.groups.add(self.craftsmen_group)
        self.client.force_login(craftsman)

        response = self.client.post(
            reverse("api-job-list"),
            data={
                "title": "Install lamp",
                "description": "Need a lamp installed.",
                "city": "Sofia",
                "budget_min": "40.00",
                "budget_max": "80.00",
                "preferred_date": str(timezone.localdate() + timedelta(days=4)),
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_create_job_via_api(self):
        response = self.client.post(
            reverse("api-job-list"),
            data={
                "title": "Install lamp",
                "description": "Need a lamp installed.",
                "city": "Sofia",
                "budget_min": "40.00",
                "budget_max": "80.00",
                "preferred_date": str(timezone.localdate() + timedelta(days=4)),
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_job_owner_can_access_job_detail_via_api(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("api-job-detail", kwargs={"pk": self.job_request.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Paint bedroom")

    def test_non_owner_non_craftsman_cannot_access_job_detail_via_api(self):
        self.client.force_login(self.other_client)

        response = self.client.get(reverse("api-job-detail", kwargs={"pk": self.job_request.pk}))

        self.assertEqual(response.status_code, 403)
