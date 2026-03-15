from django.test import TestCase

from accounts.models import User
from services.models import Category, Skill

from .models import CraftsmanProfile


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
