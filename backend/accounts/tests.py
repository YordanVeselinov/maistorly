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

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="StrongPass12345!",
        )

        response = self.client.post(
            reverse("accounts:register"),
            data={
                "username": "newclient",
                "email": "existing@example.com",
                "password1": "StrongPass12345!",
                "password2": "StrongPass12345!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with this email already exists.")


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

    def test_profile_edit_only_updates_logged_in_user_customer_account(self):
        current_user = User.objects.create_user(
            username="currentuser",
            email="current@example.com",
            password="StrongPass12345!",
        )
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="StrongPass12345!",
        )
        CustomerAccount.objects.create(user=other_user, city="Plovdiv", country="Bulgaria")

        self.client.force_login(current_user)
        response = self.client.post(
            reverse("accounts:profile_edit"),
            data={
                "phone": "+359888000000",
                "address_line1": "Main street 1",
                "address_line2": "Floor 2",
                "city": "Sofia",
                "state": "Sofia City Province",
                "postal_code": "1000",
                "country": "Bulgaria",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(CustomerAccount.objects.get(user=current_user).city, "Sofia")
        self.assertEqual(CustomerAccount.objects.get(user=other_user).city, "Plovdiv")

    def test_profile_edit_shows_user_friendly_phone_validation_error(self):
        user = User.objects.create_user(
            username="validationuser",
            email="validation@example.com",
            password="StrongPass12345!",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts:profile_edit"),
            data={
                "phone": "invalid-phone***",
                "city": "Sofia",
                "country": "Bulgaria",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Enter a valid phone number using digits, spaces, and + ( ) - symbols only.",
        )


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
