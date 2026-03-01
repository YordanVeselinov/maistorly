from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self) -> None:
        from .signals import create_default_groups

        create_default_groups(self)
