from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView

from accounts.signals import CRAFTSMEN_GROUP

from .forms import CraftsmanProfileForm
from .models import CraftsmanProfile


class CraftsmanGroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name=CRAFTSMEN_GROUP).exists()


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
