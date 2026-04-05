from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import CustomerAccountForm, EmailAuthenticationForm, RegisterForm
from .models import CustomerAccount
from .signals import CLIENTS_GROUP


class HomeView(TemplateView):
    template_name = "home.html"


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        self.object = form.save()
        client_group, _ = Group.objects.get_or_create(name=CLIENTS_GROUP)
        self.object.groups.add(client_group)
        CustomerAccount.objects.get_or_create(user=self.object)
        return redirect(self.get_success_url())


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_account, _ = CustomerAccount.objects.get_or_create(user=self.request.user)
        context["customer_account"] = customer_account
        context["primary_group"] = self.request.user.groups.order_by("name").first()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = CustomerAccountForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        customer_account, _ = CustomerAccount.objects.get_or_create(user=self.request.user)
        return customer_account

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)




class AccountLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("home")
