from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import RegisterForm, EmailAuthenticationForm
from .signals import CLIENTS_GROUP


class HomeView(TemplateView):
    template_name = "home.html"


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save()
        client_group, _ = Group.objects.get_or_create(name=CLIENTS_GROUP)
        user.groups.add(client_group)
        return redirect(self.get_success_url())


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"


class AccountLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("home")
