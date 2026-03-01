from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        user = form.save()
        client_group, _ = Group.objects.get_or_create(name="Clients")
        user.groups.add(client_group)
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(self.get_success_url())


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"


class AccountLogoutView(LogoutView):
    template_name = "accounts/logged_out.html"
