from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ResidentialUnitsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "buzztialab.apps.residential_units"
    verbose_name = _("Residential Units")
