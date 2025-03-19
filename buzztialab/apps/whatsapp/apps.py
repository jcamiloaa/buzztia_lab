from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WhatsappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "buzztialab.apps.whatsapp"
    verbose_name = _("Whatsapp")
