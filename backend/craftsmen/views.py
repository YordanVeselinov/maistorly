from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.signals import CRAFTSMEN_GROUP

from .forms import CraftsmanProfileForm, ServiceListingCreateForm, ServiceListingUpdateForm
from .models import CraftsmanProfile, ServiceListing, ServiceListingImage


class CraftsmanGroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name=CRAFTSMEN_GROUP).exists()


class NonCraftsmanOrAnonymousRequiredMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return True

        return not user.groups.filter(name=CRAFTSMEN_GROUP).exists()


class CraftsmanListView(ListView):
    model = CraftsmanProfile
    template_name = "craftsmen/craftsman_list.html"
    context_object_name = "craftsmen"

    def get_queryset(self):
        return (
            CraftsmanProfile.objects.select_related("user")
            .prefetch_related("skills")
            .filter(user__groups__name=CRAFTSMEN_GROUP)
            .distinct()
        )


class CraftsmanDetailView(DetailView):
    model = CraftsmanProfile
    template_name = "craftsmen/craftsman_detail.html"
    context_object_name = "craftsman"

    def get_queryset(self):
        return (
            CraftsmanProfile.objects.select_related("user")
            .prefetch_related("skills")
            .filter(user__groups__name=CRAFTSMEN_GROUP)
            .distinct()
        )


class CraftsmanProfileEditView(CraftsmanGroupRequiredMixin, UpdateView):
    form_class = CraftsmanProfileForm
    template_name = "craftsmen/craftsman_form.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        profile, _ = CraftsmanProfile.objects.get_or_create(user=self.request.user)
        return profile

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get("pk") is not None and kwargs["pk"] != request.user.pk:
            raise Http404("You cannot edit another craftsman profile.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Craftsman Profile"
        context["submit_label"] = "Save profile"
        return context


class ServiceListingImageUploadMixin:
    def _save_uploaded_images(self, listing, images):
        for image_file in images:
            ServiceListingImage.objects.create(listing=listing, image=image_file)


class ServiceListingListView(NonCraftsmanOrAnonymousRequiredMixin, ListView):
    model = ServiceListing
    template_name = "craftsmen/service_listing_list.html"
    context_object_name = "service_listings"

    def get_queryset(self):
        return ServiceListing.objects.select_related("craftsman", "category").prefetch_related(
            "skills",
            "images",
        )


class ServiceListingDetailView(NonCraftsmanOrAnonymousRequiredMixin, DetailView):
    model = ServiceListing
    template_name = "craftsmen/service_listing_detail.html"
    context_object_name = "service_listing"

    def get_queryset(self):
        return ServiceListing.objects.select_related("craftsman", "category").prefetch_related(
            "skills",
            "images",
        )


class ServiceListingCreateView(CraftsmanGroupRequiredMixin, ServiceListingImageUploadMixin, CreateView):
    model = ServiceListing
    form_class = ServiceListingCreateForm
    template_name = "craftsmen/service_listing_form.html"

    def form_valid(self, form):
        form.instance.craftsman = self.request.user
        response = super().form_valid(form)
        self._save_uploaded_images(self.object, form.cleaned_data.get("images", []))
        return response

    def get_success_url(self):
        return reverse("craftsmen:my_service_listings")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Service Listing"
        context["submit_label"] = "Create service listing"
        return context


class ServiceListingUpdateView(CraftsmanGroupRequiredMixin, ServiceListingImageUploadMixin, UpdateView):
    model = ServiceListing
    form_class = ServiceListingUpdateForm
    template_name = "craftsmen/service_listing_form.html"

    def get_queryset(self):
        return ServiceListing.objects.filter(craftsman=self.request.user).select_related(
            "category",
        ).prefetch_related("skills", "images")

    def form_valid(self, form):
        form.instance.craftsman = self.request.user
        response = super().form_valid(form)
        self._save_uploaded_images(self.object, form.cleaned_data.get("images", []))
        return response

    def get_success_url(self):
        return reverse("craftsmen:my_service_listings")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Service Listing"
        context["submit_label"] = "Save changes"
        return context


class ServiceListingDeleteView(CraftsmanGroupRequiredMixin, DeleteView):
    model = ServiceListing
    template_name = "craftsmen/service_listing_confirm_delete.html"
    success_url = reverse_lazy("craftsmen:my_service_listings")

    def get_queryset(self):
        return ServiceListing.objects.filter(craftsman=self.request.user)


class MyServiceListingListView(CraftsmanGroupRequiredMixin, ListView):
    model = ServiceListing
    template_name = "craftsmen/my_service_listings.html"
    context_object_name = "service_listings"

    def get_queryset(self):
        return ServiceListing.objects.filter(craftsman=self.request.user).select_related(
            "category",
        ).prefetch_related("skills", "images")
