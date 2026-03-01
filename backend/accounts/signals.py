from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate


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
