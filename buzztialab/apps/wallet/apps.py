from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WalletConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "buzztialab.apps.wallet"
    verbose_name = _("Wallet")
