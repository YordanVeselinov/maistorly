from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save


GROUPS_PERMISSIONS = {
    "Clients": [
        "view_customeraccount",
    ],
    "Craftsmen": [
        "view_customeraccount",
        "change_customeraccount",
    ],
}


def _ensure_groups(sender, **kwargs):
    for group_name, codenames in GROUPS_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        permissions = Permission.objects.filter(codename__in=codenames)
        group.permissions.set(permissions)


def create_default_groups(app_config) -> None:
    post_migrate.connect(
        _ensure_groups,
        sender=app_config,
        dispatch_uid="accounts.create_default_groups",
    )

    def _assign_group_on_registration(sender, instance, created, **kwargs):
        if not created:
            return
        if instance.is_staff or instance.is_superuser:
            return

        group, _ = Group.objects.get_or_create(name="Clients")
        instance.groups.add(group)

    user_model = apps.get_model(settings.AUTH_USER_MODEL)
    post_save.connect(
        _assign_group_on_registration,
        sender=user_model,
        dispatch_uid="accounts.assign_clients_group_on_user_create",
    )
