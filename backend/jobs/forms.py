from django import forms
from django.utils import timezone

from .models import JobRequest, Offer


class BaseJobRequestForm(forms.ModelForm):
    class Meta:
        model = JobRequest
        fields = (
            "title",
            "description",
            "city",
            "budget_min",
            "budget_max",
            "preferred_date",
            "categories",
            "required_skills",
        )
        labels = {
            "title": "Job title",
            "description": "Problem description",
            "city": "City",
            "budget_min": "Minimum budget",
            "budget_max": "Maximum budget",
            "preferred_date": "Preferred date",
            "categories": "Categories",
            "required_skills": "Required skills",
        }
        help_texts = {
            "title": "Use a short and specific title so craftsmen can quickly understand the job.",
            "description": "Describe the issue, the work needed, and any important details.",
            "city": "Enter the city where the repair job will be done.",
            "budget_min": "Enter the minimum amount you are prepared to pay.",
            "budget_max": "Enter the maximum amount you are prepared to pay.",
            "preferred_date": "Choose the earliest suitable date for the work.",
            "categories": "Select the service categories related to this job request.",
            "required_skills": "Select any specific skills a craftsman should have.",
        }
        error_messages = {
            "title": {
                "required": "Please enter a title for your job request.",
                "max_length": "Job title must be at most 200 characters long.",
            },
            "description": {
                "required": "Please describe the repair work you need.",
            },
            "city": {
                "required": "Please enter the city for this job request.",
                "max_length": "City must be at most 100 characters long.",
            },
            "budget_min": {
                "required": "Please enter a minimum budget.",
            },
            "budget_max": {
                "required": "Please enter a maximum budget.",
            },
            "preferred_date": {
                "required": "Please choose a preferred date.",
                "invalid": "Enter a valid preferred date.",
            },
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Leaking kitchen sink",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Describe the problem, what has already been tried, and any access details.",
                    "rows": 5,
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sofia",
                }
            ),
            "budget_min": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "100.00",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "budget_max": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "250.00",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "preferred_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "categories": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),
            "required_skills": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean_title(self):
        return self.cleaned_data.get("title", "").strip()

    def clean_description(self):
        return self.cleaned_data.get("description", "").strip()

    def clean_city(self):
        return self.cleaned_data.get("city", "").strip()

    def clean_budget_min(self):
        budget_min = self.cleaned_data.get("budget_min")
        if budget_min is not None and budget_min < 0:
            raise forms.ValidationError("Minimum budget cannot be negative.")
        return budget_min

    def clean_budget_max(self):
        budget_max = self.cleaned_data.get("budget_max")
        if budget_max is not None and budget_max < 0:
            raise forms.ValidationError("Maximum budget cannot be negative.")
        return budget_max

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data.get("preferred_date")
        if preferred_date and preferred_date < timezone.localdate():
            raise forms.ValidationError("Preferred date cannot be in the past.")
        return preferred_date

    def clean(self):
        cleaned_data = super().clean()
        budget_min = cleaned_data.get("budget_min")
        budget_max = cleaned_data.get("budget_max")

        if (
            budget_min is not None
            and budget_max is not None
            and budget_max < budget_min
        ):
            self.add_error(
                "budget_max",
                "Maximum budget cannot be less than minimum budget.",
            )

        return cleaned_data


class JobRequestCreateForm(BaseJobRequestForm):
    pass


class JobRequestUpdateForm(BaseJobRequestForm):
    owner_username = forms.CharField(
        label="Job owner",
        required=False,
        disabled=True,
        help_text="This field is read-only and is shown for reference only.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Job owner",
                "readonly": True,
            }
        ),
    )

    class Meta(BaseJobRequestForm.Meta):
        fields = BaseJobRequestForm.Meta.fields + ("status",)
        labels = {
            **BaseJobRequestForm.Meta.labels,
            "status": "Job status",
        }
        help_texts = {
            **BaseJobRequestForm.Meta.help_texts,
            "status": "Update the current progress of your job request.",
        }
        error_messages = {
            **BaseJobRequestForm.Meta.error_messages,
            "status": {
                "required": "Please choose the current status for this job request.",
            },
        }
        widgets = {
            **BaseJobRequestForm.Meta.widgets,
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(
            [
                "owner_username",
                "title",
                "description",
                "city",
                "budget_min",
                "budget_max",
                "preferred_date",
                "status",
                "categories",
                "required_skills",
            ]
        )
        if self.instance and self.instance.owner_id:
            self.fields["owner_username"].initial = self.instance.owner.get_username()


class OfferCreateForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = (
            "message",
            "proposed_price",
            "estimated_days",
        )
        labels = {
            "message": "Offer message",
            "proposed_price": "Proposed price",
            "estimated_days": "Estimated days",
        }
        help_texts = {
            "message": "Briefly explain your approach, availability, and any relevant experience.",
            "proposed_price": "Enter the total price you propose for completing the job.",
            "estimated_days": "Enter how many days you expect the job to take.",
        }
        error_messages = {
            "message": {
                "required": "Please enter a message for your offer.",
            },
            "proposed_price": {
                "required": "Please enter your proposed price.",
            },
            "estimated_days": {
                "required": "Please enter the estimated number of days.",
                "invalid": "Enter a valid number of estimated days.",
            },
        }
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "I can inspect the issue this week and complete the repair with included materials.",
                    "rows": 5,
                }
            ),
            "proposed_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "180.00",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "estimated_days": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "2",
                    "min": "1",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.craftsman = kwargs.pop("craftsman", None)
        self.job_request = kwargs.pop("job_request", None)
        super().__init__(*args, **kwargs)

    def clean_message(self):
        return self.cleaned_data.get("message", "").strip()

    def clean_proposed_price(self):
        proposed_price = self.cleaned_data.get("proposed_price")
        if proposed_price is not None and proposed_price < 0:
            raise forms.ValidationError("Proposed price cannot be negative.")
        return proposed_price

    def clean_estimated_days(self):
        estimated_days = self.cleaned_data.get("estimated_days")
        if estimated_days is not None and estimated_days < 1:
            raise forms.ValidationError("Estimated days must be at least 1.")
        return estimated_days

    def clean(self):
        cleaned_data = super().clean()
        job_request = self.job_request or getattr(self.instance, "job_request", None)

        if self.craftsman and job_request and self.craftsman == job_request.owner:
            raise forms.ValidationError(
                "You cannot submit an offer for your own job request."
            )

        return cleaned_data

    def save(self, commit=True):
        offer = super().save(commit=False)
        if self.job_request is not None:
            offer.job_request = self.job_request
        if self.craftsman is not None:
            offer.craftsman = self.craftsman
        if commit:
            offer.save()
            self.save_m2m()
        return offer


class JobRequestDeleteConfirmForm(forms.Form):
    title = forms.CharField(
        label="Job request",
        required=False,
        disabled=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "readonly": True,
            }
        ),
    )
    confirm = forms.BooleanField(
        label="Confirm deletion",
        help_text="Tick this box to permanently delete the selected job request.",
        error_messages={
            "required": "Please confirm that you want to delete this job request.",
        },
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)
        if instance is not None:
            self.fields["title"].initial = instance.title


class OfferDeleteConfirmForm(forms.Form):
    offer_summary = forms.CharField(
        label="Offer",
        required=False,
        disabled=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "readonly": True,
            }
        ),
    )
    confirm = forms.BooleanField(
        label="Confirm deletion",
        help_text="Tick this box to permanently delete the selected offer.",
        error_messages={
            "required": "Please confirm that you want to delete this offer.",
        },
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)
        if instance is not None:
            self.fields["offer_summary"].initial = str(instance)
