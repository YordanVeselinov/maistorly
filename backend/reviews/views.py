from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from craftsmen.models import CraftsmanProfile
from jobs.models import JobRequest

from .forms import ReviewCreateForm, ReviewDeleteConfirmForm, ReviewUpdateForm
from .models import Review


class ReviewCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Review
    form_class = ReviewCreateForm
    template_name = "reviews/review_form.html"
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        self.job_request = get_object_or_404(JobRequest.objects.select_related("owner"), pk=kwargs["job_pk"])
        self.craftsman_profile = get_object_or_404(
            CraftsmanProfile.objects.select_related("user"),
            pk=kwargs["craftsman_pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return (
            self.request.user == self.job_request.owner
            and self.job_request.status == JobRequest.Status.COMPLETED
            and self.job_request.offers.filter(craftsman=self.craftsman_profile.user).exists()
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["job_request"] = self.job_request
        kwargs["reviewer"] = self.request.user
        kwargs["craftsman"] = self.craftsman_profile.user
        return kwargs

    def get_success_url(self):
        return reverse("jobs:job_detail", kwargs={"pk": self.job_request.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_request"] = self.job_request
        context["craftsman_profile"] = self.craftsman_profile
        context["page_title"] = "Create Review"
        context["submit_label"] = "Publish review"
        return context


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewUpdateForm
    template_name = "reviews/review_form.html"
    raise_exception = True

    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user).select_related(
            "job_request",
            "craftsman",
        )

    def test_func(self):
        return self.get_object().reviewer == self.request.user

    def get_success_url(self):
        craftsman_profile = CraftsmanProfile.objects.filter(user=self.object.craftsman).first()
        if craftsman_profile is not None:
            return reverse("reviews:craftsman_reviews", kwargs={"pk": craftsman_profile.pk})
        return reverse("jobs:job_detail", kwargs={"pk": self.object.job_request.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_request"] = self.object.job_request
        context["craftsman_profile"] = CraftsmanProfile.objects.filter(user=self.object.craftsman).first()
        context["page_title"] = "Edit Review"
        context["submit_label"] = "Save review"
        return context


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    form_class = ReviewDeleteConfirmForm
    template_name = "reviews/review_confirm_delete.html"
    raise_exception = True

    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user).select_related(
            "job_request",
            "craftsman",
        )

    def test_func(self):
        return self.get_object().reviewer == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def get_success_url(self):
        craftsman_profile = CraftsmanProfile.objects.filter(user=self.object.craftsman).first()
        if craftsman_profile is not None:
            return reverse("reviews:craftsman_reviews", kwargs={"pk": craftsman_profile.pk})
        return reverse_lazy("jobs:job_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["review"] = self.object
        return context


class ReviewListByCraftsmanView(ListView):
    model = Review
    template_name = "reviews/craftsman_reviews.html"
    context_object_name = "reviews"

    def dispatch(self, request, *args, **kwargs):
        self.craftsman_profile = get_object_or_404(
            CraftsmanProfile.objects.select_related("user").prefetch_related("skills"),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Review.objects.filter(craftsman=self.craftsman_profile.user).select_related(
            "reviewer",
            "job_request",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["craftsman_profile"] = self.craftsman_profile
        context["average_rating"] = (
            sum(review.rating for review in context["reviews"]) / len(context["reviews"])
            if context["reviews"]
            else None
        )
        return context
