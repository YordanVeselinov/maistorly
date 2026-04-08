from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group
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
        self.owner.groups.add(self.clients_group)
        self.other_user.groups.add(self.clients_group)
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

    def test_authenticated_user_can_create_job_request_and_becomes_owner(self):
        self.client.force_login(self.other_user)

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
            },
        )

        self.assertEqual(response.status_code, 302)
        job_request = JobRequest.objects.get(title="Install faucet")
        self.assertEqual(job_request.owner, self.other_user)

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


class JobApiTests(TestCase):
    def setUp(self):
        self.clients_group, _ = Group.objects.get_or_create(name=CLIENTS_GROUP)
        self.craftsmen_group, _ = Group.objects.get_or_create(name=CRAFTSMEN_GROUP)
        self.owner = User.objects.create_user(
            username="apiowner",
            email="apiowner@example.com",
            password="StrongPass12345!",
        )
        self.owner.groups.add(self.clients_group)
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

    def test_jobs_list_api_returns_public_data(self):
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
