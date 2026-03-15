from django.test import TestCase

from .models import Category, Skill


class ServiceModelsTests(TestCase):
    def test_category_slug_is_generated_from_name(self):
        category = Category.objects.create(name="Home Repair")

        self.assertEqual(category.slug, "home-repair")

    def test_skill_slug_is_generated_from_name(self):
        category = Category.objects.create(name="Electrical")
        skill = Skill.objects.create(category=category, name="Light Installation")

        self.assertEqual(skill.slug, "light-installation")
