from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator

from .models import CustomerAccount, User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter your email"})
    )


class CustomerAccountForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email address",
        required=False,
        disabled=True,
        help_text="This email is linked to your account and cannot be changed here.",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your email address",
                "readonly": True,
            }
        ),
    )

    class Meta:
        model = CustomerAccount
        fields = (
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
        )
        labels = {
            "phone": "Phone number",
            "address_line1": "Address line 1",
            "address_line2": "Address line 2",
            "city": "City",
            "state": "State / Region",
            "postal_code": "Postal code",
            "country": "Country",
        }
        help_texts = {
            "phone": "Optional. Include country code if needed.",
            "address_line1": "Optional. Street name, number, building, or area.",
            "address_line2": "Optional. Apartment, floor, entrance, or landmark.",
            "city": "Optional. Enter your current city.",
            "state": "Optional. Enter your state, province, or region.",
            "postal_code": "Optional. Enter your ZIP or postal code.",
            "country": "Optional. Enter your current country.",
        }
        error_messages = {
            "phone": {
                "max_length": "Phone number must be at most 32 characters long.",
            },
            "address_line1": {
                "max_length": "Address line 1 must be at most 200 characters long.",
            },
            "address_line2": {
                "max_length": "Address line 2 must be at most 200 characters long.",
            },
            "city": {
                "max_length": "City must be at most 100 characters long.",
            },
            "state": {
                "max_length": "State / Region must be at most 100 characters long.",
            },
            "postal_code": {
                "max_length": "Postal code must be at most 32 characters long.",
            },
            "country": {
                "max_length": "Country must be at most 100 characters long.",
            },
        }
        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+359 888 123 456",
                }
            ),
            "address_line1": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Street and number",
                }
            ),
            "address_line2": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Apartment, floor, or landmark",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sofia",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sofia City Province",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "1000",
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Bulgaria",
                }
            ),
        }

    phone_validator = RegexValidator(
        regex=r"^[0-9+()\-\s]{7,32}$",
        message="Enter a valid phone number using digits, spaces, and + ( ) - symbols only.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(
            [
                "email",
                "phone",
                "address_line1",
                "address_line2",
                "city",
                "state",
                "postal_code",
                "country",
            ]
        )
        if self.instance and self.instance.user_id:
            self.fields["email"].initial = self.instance.user.email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return ""

        self.phone_validator(phone)
        return phone

    def clean_address_line1(self):
        return self.cleaned_data.get("address_line1", "").strip()

    def clean_address_line2(self):
        return self.cleaned_data.get("address_line2", "").strip()

    def clean_city(self):
        return self.cleaned_data.get("city", "").strip()

    def clean_state(self):
        return self.cleaned_data.get("state", "").strip()

    def clean_postal_code(self):
        return self.cleaned_data.get("postal_code", "").strip()

    def clean_country(self):
        return self.cleaned_data.get("country", "").strip()
