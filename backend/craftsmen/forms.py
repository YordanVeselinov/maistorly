from django import forms
from django.core.validators import RegexValidator

from .models import CraftsmanProfile, ServiceListing


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageFileField(forms.FileField):
    def clean(self, data, initial=None):
        cleaned_files = []
        single_file_clean = super().clean

        if not data:
            return cleaned_files

        if isinstance(data, (list, tuple)):
            for uploaded_file in data:
                cleaned_files.append(single_file_clean(uploaded_file, initial))
            return cleaned_files

        cleaned_files.append(single_file_clean(data, initial))
        return cleaned_files


class CraftsmanProfileForm(forms.ModelForm):
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
        model = CraftsmanProfile
        fields = (
            "display_name",
            "email",
            "bio",
            "phone",
            "city",
            "country",
            "skills",
            "is_available",
        )
        labels = {
            "display_name": "Display name",
            "bio": "Short bio",
            "phone": "Phone number",
            "city": "City",
            "country": "Country",
            "skills": "Skills",
            "is_available": "Available for work",
        }
        help_texts = {
            "display_name": "Optional. Leave empty to use your username publicly.",
            "bio": "Optional. Briefly describe your experience and the type of work you do.",
            "phone": "Optional. Include country code if needed.",
            "city": "Optional. Enter the city where you usually work.",
            "country": "Optional. Enter the country where you offer services.",
            "skills": "Select the skills you want to show on your public profile.",
            "is_available": "Uncheck this if you are not currently accepting new jobs.",
        }
        error_messages = {
            "display_name": {
                "max_length": "Display name must be at most 120 characters long.",
            },
            "phone": {
                "max_length": "Phone number must be at most 32 characters long.",
            },
            "city": {
                "max_length": "City must be at most 100 characters long.",
            },
            "country": {
                "max_length": "Country must be at most 100 characters long.",
            },
        }
        widgets = {
            "display_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ivan Petrov",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Experienced electrician specialising in residential repairs and installations.",
                    "rows": 5,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+359 888 123 456",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sofia",
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Bulgaria",
                }
            ),
            "skills": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),
            "is_available": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
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
                "display_name",
                "email",
                "bio",
                "phone",
                "city",
                "country",
                "skills",
                "is_available",
            ]
        )
        if self.instance and self.instance.user_id:
            self.fields["email"].initial = self.instance.user.email

    def clean_display_name(self):
        return self.cleaned_data.get("display_name", "").strip()

    def clean_bio(self):
        return self.cleaned_data.get("bio", "").strip()

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return ""

        self.phone_validator(phone)
        return phone

    def clean_city(self):
        return self.cleaned_data.get("city", "").strip()

    def clean_country(self):
        return self.cleaned_data.get("country", "").strip()


class BaseServiceListingForm(forms.ModelForm):
    images = MultipleImageFileField(
        label="Work images",
        required=False,
        help_text="Optional. Upload one or more images that showcase your work.",
        widget=MultipleFileInput(
            attrs={
                "class": "form-control",
                "accept": ".jpg,.jpeg,.png,.webp",
            }
        ),
    )

    class Meta:
        model = ServiceListing
        fields = (
            "title",
            "description",
            "rough_price",
            "category",
            "skills",
            "images",
        )
        labels = {
            "title": "Service title",
            "description": "Service description",
            "rough_price": "Rough starting price",
            "category": "Category",
            "skills": "Skills",
        }
        help_texts = {
            "title": "Use a clear title describing the type of work you offer.",
            "description": "Explain what the service includes and key details clients should know.",
            "rough_price": "Enter an approximate starting price for this service.",
            "category": "Optional. Select the main category for this listing.",
            "skills": "Optional. Select related skills for better discoverability.",
        }
        error_messages = {
            "title": {
                "required": "Please enter a title for your service listing.",
                "max_length": "Service title must be at most 200 characters long.",
            },
            "description": {
                "required": "Please provide a description of your service.",
            },
            "rough_price": {
                "required": "Please enter a rough starting price.",
                "invalid": "Enter a valid price amount.",
            },
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Kitchen sink installation",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "I install and replace kitchen sinks, including drain and faucet connection.",
                    "rows": 5,
                }
            ),
            "rough_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "120.00",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "skills": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean_title(self):
        return self.cleaned_data.get("title", "").strip()

    def clean_description(self):
        return self.cleaned_data.get("description", "").strip()

    def clean_rough_price(self):
        rough_price = self.cleaned_data.get("rough_price")
        if rough_price is not None and rough_price < 0:
            raise forms.ValidationError("Rough starting price cannot be negative.")
        return rough_price


class ServiceListingCreateForm(BaseServiceListingForm):
    pass


class ServiceListingUpdateForm(BaseServiceListingForm):
    pass
