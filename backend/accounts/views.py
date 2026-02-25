from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm


@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            client_group, _ = Group.objects.get_or_create(name="Clients")
            user.groups.add(client_group)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("admin:index")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})
