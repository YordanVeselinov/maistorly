from django import forms

from jobs.models import Offer

from .models import Review


class BaseReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
        labels = {
            "rating": "Rating",
            "comment": "Comment",
        }
        help_texts = {
            "rating": "Give a rating from 1 to 5.",
            "comment": "Describe your experience working with this craftsman.",
        }
        error_messages = {
            "rating": {
                "required": "Please select a rating.",
            },
            "comment": {
                "required": "Please enter a review comment.",
            },
        }
        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "max": "5",
                    "step": "1",
                    "placeholder": "5",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Share your experience with the completed work.",
                }
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if rating is not None and not 1 <= rating <= 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating

    def clean_comment(self):
        return self.cleaned_data.get("comment", "").strip()


class ReviewCreateForm(BaseReviewForm):
    craftsman_name = forms.CharField(
        label="Craftsman",
        required=False,
        disabled=True,
        help_text="This field is read-only and is shown for reference only.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "readonly": True,
            }
        ),
    )

    class Meta(BaseReviewForm.Meta):
        fields = ("rating", "comment")

    def __init__(self, *args, **kwargs):
        self.job_request = kwargs.pop("job_request", None)
        self.reviewer = kwargs.pop("reviewer", None)
        self.craftsman = kwargs.pop("craftsman", None)
        super().__init__(*args, **kwargs)
        self.order_fields(["craftsman_name", "rating", "comment"])
        if self.craftsman is not None:
            self.fields["craftsman_name"].initial = self.craftsman.get_username()

    def clean(self):
        cleaned_data = super().clean()
        if self.job_request is not None and self.job_request.status != self.job_request.Status.COMPLETED:
            raise forms.ValidationError("You can only create a review after the job is completed.")

        if self.job_request is not None and self.reviewer is not None and self.job_request.owner != self.reviewer:
            raise forms.ValidationError("Only the job owner can create a review for this job request.")

        if (
            self.job_request is not None
            and self.reviewer is not None
            and self.craftsman is not None
            and Review.objects.filter(
                job_request=self.job_request,
                reviewer=self.reviewer,
                craftsman=self.craftsman,
            ).exists()
        ):
            raise forms.ValidationError("You have already reviewed this craftsman for this job request.")

        if (
            self.job_request is not None
            and self.craftsman is not None
            and not Offer.objects.filter(
                job_request=self.job_request,
                craftsman=self.craftsman,
            ).exists()
        ):
            raise forms.ValidationError(
                "You can only review a craftsman who has submitted an offer for this job request."
            )

        return cleaned_data

    def save(self, commit=True):
        review = super().save(commit=False)
        if self.job_request is not None:
            review.job_request = self.job_request
        if self.reviewer is not None:
            review.reviewer = self.reviewer
        if self.craftsman is not None:
            review.craftsman = self.craftsman
        if commit:
            review.save()
        return review


class ReviewUpdateForm(BaseReviewForm):
    craftsman_name = forms.CharField(
        label="Craftsman",
        required=False,
        disabled=True,
        help_text="This field is read-only and cannot be changed.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "readonly": True,
            }
        ),
    )

    class Meta(BaseReviewForm.Meta):
        fields = ("rating", "comment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(["craftsman_name", "rating", "comment"])
        if self.instance and self.instance.craftsman_id:
            self.fields["craftsman_name"].initial = self.instance.craftsman.get_username()


class ReviewDeleteConfirmForm(forms.Form):
    review_summary = forms.CharField(
        label="Review",
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
        help_text="Tick this box to permanently delete the selected review.",
        error_messages={
            "required": "Please confirm that you want to delete this review.",
        },
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)
        if instance is not None:
            self.fields["review_summary"].initial = str(instance)
