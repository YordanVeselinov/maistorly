from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView

from .forms import CategoryCreateForm, SkillCreateForm
from .models import Category, Skill


class ReturnToNextMixin:
    fallback_url = reverse_lazy("home")

    def get_next_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return self.fallback_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.get_next_url()
        return context

    def get_success_url(self):
        return self.get_next_url()


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, ReturnToNextMixin, CreateView):
    model = Category
    form_class = CategoryCreateForm
    template_name = "services/taxonomy_form.html"
    success_message = "Category created."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add Category"
        context["page_subtitle"] = "Create a category that can be used in listings and job requests."
        context["submit_label"] = "Create category"
        return context


class SkillCreateView(LoginRequiredMixin, SuccessMessageMixin, ReturnToNextMixin, CreateView):
    model = Skill
    form_class = SkillCreateForm
    template_name = "services/taxonomy_form.html"
    success_message = "Skill created."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add Skill"
        context["page_subtitle"] = "Create a skill that can be used in listings and job requests."
        context["submit_label"] = "Create skill"
        return context
