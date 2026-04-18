from django.test import TestCase

from .models import Category, Skill


class ServiceModelsTests(TestCase):
    def test_category_slug_is_generated_from_name(self):
        category = Category.objects.create(name="Home Repair")

        self.assertEqual(category.slug, "home-repair")

    def test_skill_slug_is_generated_from_name(self):
        category = Category.objects.create(name="Test Electrical")
        skill = Skill.objects.create(category=category, name="Test Light Installation")

        self.assertEqual(skill.slug, "test-light-installation")
