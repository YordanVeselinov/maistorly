from django.test import TestCase
from django.urls import reverse

from .models import User


class RegisterViewTests(TestCase):
    def test_register_assigns_clients_group_by_default(self):
        response = self.client.post(
            reverse("accounts:register"),
            data={
                "username": "newclient",
                "email": "newclient@example.com",
                "password1": "StrongPass12345!",
                "password2": "StrongPass12345!",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newclient")
        self.assertTrue(user.groups.filter(name="Clients").exists())
        self.assertFalse(user.groups.filter(name="Craftsmen").exists())

    def test_register_page_renders(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
