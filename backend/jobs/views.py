from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.signals import CRAFTSMEN_GROUP

from .forms import (
    JobRequestCreateForm,
    JobRequestDeleteConfirmForm,
    JobRequestUpdateForm,
    OfferCreateForm,
)
from .models import JobRequest, Offer
from craftsmen.models import CraftsmanProfile
from reviews.models import Review
from services.models import Category
from .tasks import send_offer_notification_email


class CraftsmanRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name=CRAFTSMEN_GROUP).exists()


class JobRequestListView(ListView):
    model = JobRequest
    template_name = "jobs/job_list.html"
    context_object_name = "job_requests"

    def get_queryset(self):
        queryset = (
            JobRequest.objects.select_related("owner")
            .prefetch_related("categories", "required_skills")
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


class JobRequestDetailView(DetailView):
    model = JobRequest
    template_name = "jobs/job_detail.html"
    context_object_name = "job_request"

    def get_queryset(self):
        return JobRequest.objects.select_related("owner").prefetch_related(
            "categories",
            "required_skills",
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
        return context


class JobRequestCreateView(LoginRequiredMixin, CreateView):
    model = JobRequest
    form_class = JobRequestCreateForm
    template_name = "jobs/job_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:job_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Job Request"
        context["submit_label"] = "Create job request"
        return context


class JobRequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = JobRequest
    form_class = JobRequestUpdateForm
    template_name = "jobs/job_form.html"
    raise_exception = True

    def get_queryset(self):
        return JobRequest.objects.filter(owner=self.request.user).prefetch_related(
            "categories",
            "required_skills",
        )

    def test_func(self):
        return self.get_object().owner == self.request.user

    def get_success_url(self):
        return reverse("jobs:job_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Job Request"
        context["submit_label"] = "Save changes"
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


class MyJobRequestListView(LoginRequiredMixin, ListView):
    model = JobRequest
    template_name = "jobs/my_jobs.html"
    context_object_name = "job_requests"

    def get_queryset(self):
        return (
            JobRequest.objects.filter(owner=self.request.user)
            .prefetch_related("categories", "required_skills")
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
        return reverse("jobs:job_detail", kwargs={"pk": self.job_request.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        send_offer_notification_email.delay(self.object.pk)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_request"] = self.job_request
        context["page_title"] = "Submit Offer"
        context["submit_label"] = "Submit offer"
        return context


class MyOffersListView(CraftsmanRequiredMixin, ListView):
    model = Offer
    template_name = "jobs/my_offers.html"
    context_object_name = "offers"

    def get_queryset(self):
        return Offer.objects.filter(craftsman=self.request.user).select_related(
            "job_request",
            "job_request__owner",
        )
