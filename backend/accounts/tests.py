from django.test import TestCase
from django.urls import reverse

from .models import CustomerAccount, User


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
        self.assertTrue(CustomerAccount.objects.filter(user=user).exists())

    def test_register_page_renders(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)


class ProfileViewTests(TestCase):
    def test_profile_page_creates_missing_customer_account(self):
        user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="StrongPass12345!",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomerAccount.objects.filter(user=user).exists())

    def test_profile_edit_updates_customer_account(self):
        user = User.objects.create_user(
            username="edituser",
            email="edit@example.com",
            password="StrongPass12345!",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts:profile_edit"),
            data={
                "phone": "+359888123456",
                "city": "Sofia",
                "country": "Bulgaria",
            },
        )

        self.assertEqual(response.status_code, 302)
        account = CustomerAccount.objects.get(user=user)
        self.assertEqual(account.phone, "+359888123456")
        self.assertEqual(account.city, "Sofia")
        self.assertEqual(account.country, "Bulgaria")


class AuthenticationFlowTests(TestCase):
    def test_login_with_email_works_for_active_user(self):
        user = User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="StrongPass12345!",
        )

        response = self.client.post(
            reverse("accounts:login"),
            data={
                "username": "login@example.com",
                "password": "StrongPass12345!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_login_with_email_fails_for_inactive_user(self):
        User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="StrongPass12345!",
            is_active=False,
        )

        response = self.client.post(
            reverse("accounts:login"),
            data={
                "username": "inactive@example.com",
                "password": "StrongPass12345!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_clears_authenticated_session(self):
        user = User.objects.create_user(
            username="logoutuser",
            email="logout@example.com",
            password="StrongPass12345!",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:profile')}",
        )
