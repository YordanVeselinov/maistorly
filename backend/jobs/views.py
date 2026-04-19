from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.base import View

from accounts.signals import CLIENTS_GROUP, CRAFTSMEN_GROUP

from .forms import (
    JobRequestCreateForm,
    JobRequestDeleteConfirmForm,
    JobRequestUpdateForm,
    OfferCreateForm,
    OfferDeleteConfirmForm,
)
from .models import JobRequest, JobRequestImage, Offer
from craftsmen.models import CraftsmanProfile
from reviews.models import Review
from services.models import Category
from .tasks import send_offer_notification_email


class ClientRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name=CLIENTS_GROUP).exists()


class CraftsmanRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name=CRAFTSMEN_GROUP).exists()


class JobRequestViewerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        if user.groups.filter(name=CRAFTSMEN_GROUP).exists():
            return True

        return self.get_object().owner == user


class JobRequestListView(CraftsmanRequiredMixin, ListView):
    model = JobRequest
    template_name = "jobs/job_list.html"
    context_object_name = "job_requests"

    def get_queryset(self):
        queryset = (
            JobRequest.objects.select_related("owner")
            .prefetch_related("categories", "required_skills", "images")
        )

        city = self.request.GET.get("city", "").strip()
        status = self.request.GET.get("status", "").strip()
        category = self.request.GET.get("category", "").strip()
        search_query = self.request.GET.get("q", "").strip()

        if city:
            queryset = queryset.filter(city__iexact=city)

        if status:
            queryset = queryset.filter(status=status)

        if category:
            queryset = queryset.filter(categories__id=category)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(city__icontains=search_query)
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["status_choices"] = JobRequest.Status.choices
        context["current_filters"] = {
            "city": self.request.GET.get("city", "").strip(),
            "status": self.request.GET.get("status", "").strip(),
            "category": self.request.GET.get("category", "").strip(),
            "q": self.request.GET.get("q", "").strip(),
        }
        return context


class JobRequestDetailView(JobRequestViewerRequiredMixin, DetailView):
    model = JobRequest
    template_name = "jobs/job_detail.html"
    context_object_name = "job_request"

    def get_queryset(self):
        return JobRequest.objects.select_related("owner").prefetch_related(
            "categories",
            "required_skills",
            "images",
            "offers__craftsman",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_authenticated = user.is_authenticated
        is_owner = is_authenticated and user == self.object.owner
        is_craftsman = is_authenticated and user.groups.filter(name=CRAFTSMEN_GROUP).exists()
        offers = list(self.object.offers.select_related("craftsman").all()) if is_owner else []
        craftsman_profiles = {
            profile.user_id: profile
            for profile in CraftsmanProfile.objects.select_related("user").filter(
                user_id__in=[offer.craftsman_id for offer in offers]
            )
        }
        existing_reviews_by_craftsman = {}

        if is_owner:
            existing_reviews = Review.objects.filter(
                    job_request=self.object,
                    reviewer=user,
                ).select_related("craftsman")
            existing_reviews_by_craftsman = {
                review.craftsman_id: review for review in existing_reviews
            }

        context["is_owner"] = is_owner
        context["can_create_offer"] = (
            is_authenticated
            and is_craftsman
            and user != self.object.owner
        )
        context["offers"] = offers
        context["offer_entries"] = [
            {
                "offer": offer,
                "craftsman_profile": craftsman_profiles.get(offer.craftsman_id),
                "review": existing_reviews_by_craftsman.get(offer.craftsman_id),
            }
            for offer in offers
        ]
        context["back_to_jobs_url"] = (
            reverse("jobs:my_jobs")
            if is_owner
            else reverse("jobs:job_list")
        )
        return context


class JobRequestImageUploadMixin:
    def _save_uploaded_images(self, job_request, images):
        for image_file in images:
            JobRequestImage.objects.create(job_request=job_request, image=image_file)


class JobRequestCreateView(ClientRequiredMixin, JobRequestImageUploadMixin, CreateView):
    model = JobRequest
    form_class = JobRequestCreateForm
    template_name = "jobs/job_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self._save_uploaded_images(self.object, form.cleaned_data.get("images", []))
        return response

    def get_success_url(self):
        return reverse("jobs:job_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Job Request"
        context["submit_label"] = "Create job request"
        context["back_url"] = reverse("jobs:my_jobs")
        return context


class JobRequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, JobRequestImageUploadMixin, UpdateView):
    model = JobRequest
    form_class = JobRequestUpdateForm
    template_name = "jobs/job_form.html"
    raise_exception = True

    def get_queryset(self):
        return JobRequest.objects.filter(owner=self.request.user).prefetch_related(
            "categories",
            "required_skills",
            "images",
        )

    def test_func(self):
        return self.get_object().owner == self.request.user

    def get_success_url(self):
        return reverse("jobs:job_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        self._save_uploaded_images(self.object, form.cleaned_data.get("images", []))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Job Request"
        context["submit_label"] = "Save changes"
        context["back_url"] = reverse("jobs:my_jobs")
        return context


class JobRequestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = JobRequest
    form_class = JobRequestDeleteConfirmForm
    template_name = "jobs/job_confirm_delete.html"
    success_url = reverse_lazy("jobs:my_jobs")
    raise_exception = True

    def get_queryset(self):
        return JobRequest.objects.filter(owner=self.request.user)

    def test_func(self):
        return self.get_object().owner == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_request"] = self.object
        return context


class MyJobRequestListView(ClientRequiredMixin, ListView):
    model = JobRequest
    template_name = "jobs/my_jobs.html"
    context_object_name = "job_requests"

    def get_queryset(self):
        return (
            JobRequest.objects.filter(owner=self.request.user)
            .prefetch_related("categories", "required_skills", "images")
        )


class OfferCreateView(CraftsmanRequiredMixin, CreateView):
    model = Offer
    form_class = OfferCreateForm
    template_name = "jobs/offer_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.job_request = JobRequest.objects.select_related("owner").filter(
            pk=kwargs["pk"]
        ).first()
        if self.job_request is None:
            raise Http404("Job request not found.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["craftsman"] = self.request.user
        kwargs["job_request"] = self.job_request
        return kwargs

    def get_success_url(self):
        return reverse("jobs:job_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        send_offer_notification_email.delay(self.object.pk)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_request"] = self.job_request
        context["page_title"] = "Submit Counter-Offer"
        context["submit_label"] = "Submit counter-offer"
        return context


class OfferDecisionView(LoginRequiredMixin, UserPassesTestMixin, View):
    action_message = "Counter-offer updated."
    raise_exception = True
    http_method_names = ["post"]

    def dispatch(self, request, *args, **kwargs):
        self.offer = (
            Offer.objects.select_related("job_request", "craftsman")
            .filter(pk=kwargs["pk"])
            .first()
        )
        if self.offer is None:
            raise Http404("Counter-offer not found.")
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        user = self.request.user
        return (
            self.offer.job_request.owner_id == user.id
            and self.offer.craftsman_id != user.id
        )

    def get_success_url(self):
        next_url = self.request.POST.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return reverse("jobs:my_received_offers")

    def post(self, request, *args, **kwargs):
        success_url = self.get_success_url()
        self.offer.delete()
        messages.success(request, self.action_message)
        return redirect(success_url)


class OfferAcceptView(OfferDecisionView):
    action_message = "Counter-offer accepted and removed."


class OfferDeclineView(OfferDecisionView):
    action_message = "Counter-offer declined and removed."


class MyOffersListView(CraftsmanRequiredMixin, ListView):
    model = Offer
    template_name = "jobs/my_offers.html"
    context_object_name = "offers"

    def get_queryset(self):
        return Offer.objects.filter(craftsman=self.request.user).select_related(
            "job_request",
            "job_request__owner",
        )


class OfferDeleteView(CraftsmanRequiredMixin, DeleteView):
    model = Offer
    form_class = OfferDeleteConfirmForm
    template_name = "jobs/offer_confirm_delete.html"
    success_url = reverse_lazy("jobs:my_offers")

    def get_queryset(self):
        return Offer.objects.filter(craftsman=self.request.user).select_related(
            "job_request",
            "job_request__owner",
        )

    def form_valid(self, form):
        messages.success(self.request, "Counter-offer deleted.")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offer"] = self.object
        return context


class MyReceivedOffersListView(ClientRequiredMixin, ListView):
    model = Offer
    template_name = "jobs/my_received_offers.html"
    context_object_name = "offers"

    def get_queryset(self):
        return Offer.objects.filter(job_request__owner=self.request.user).select_related(
            "job_request",
            "craftsman",
        )
