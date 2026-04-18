from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Category, Skill


class ServiceModelsTests(TestCase):
    def test_category_slug_is_generated_from_name(self):
        category = Category.objects.create(name="Home Repair")

        self.assertEqual(category.slug, "home-repair")

    def test_skill_slug_is_generated_from_name(self):
        category = Category.objects.create(name="Test Electrical")
        skill = Skill.objects.create(category=category, name="Test Light Installation")

        self.assertEqual(skill.slug, "test-light-installation")


class ServiceTaxonomyCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="taxonomyuser",
            email="taxonomyuser@example.com",
            password="StrongPass12345!",
        )

    def test_authenticated_user_can_create_category_and_return_to_next_url(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("services:category_create"),
            data={
                "name": "Window Repair",
                "description": "Repairs for windows and frames.",
                "next": reverse("jobs:job_create"),
            },
        )

        self.assertRedirects(
            response,
            reverse("jobs:job_create"),
            fetch_redirect_response=False,
        )
        self.assertTrue(Category.objects.filter(name="Window Repair").exists())

    def test_category_create_rejects_duplicate_name(self):
        Category.objects.create(name="Duplicate Category")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("services:category_create"),
            data={
                "name": "duplicate category",
                "description": "",
                "next": reverse("jobs:job_create"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This category already exists.")

    def test_authenticated_user_can_create_skill_and_return_to_next_url(self):
        category = Category.objects.create(name="Window Services")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("services:skill_create"),
            data={
                "category": category.pk,
                "name": "Window Sealing",
                "description": "Seal drafty windows.",
                "next": reverse("craftsmen:service_listing_create"),
            },
        )

        self.assertRedirects(
            response,
            reverse("craftsmen:service_listing_create"),
            fetch_redirect_response=False,
        )
        self.assertTrue(
            Skill.objects.filter(
                category=category,
                name="Window Sealing",
                slug="window-services-window-sealing",
            ).exists()
        )

    def test_skill_create_rejects_duplicate_name_in_same_category(self):
        category = Category.objects.create(name="Duplicate Skill Category")
        Skill.objects.create(category=category, name="Duplicate Skill")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("services:skill_create"),
            data={
                "category": category.pk,
                "name": "duplicate skill",
                "description": "",
                "next": reverse("jobs:job_create"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This skill already exists in the selected category.")
