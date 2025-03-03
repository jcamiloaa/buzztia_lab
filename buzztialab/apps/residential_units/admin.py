from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import House
from .models import Resident
from .models import ResidentialUnit


@admin.register(ResidentialUnit)
class ResidentialUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "property_type", "status", "is_active", "created_at")
    list_filter = ("property_type", "status", "is_active")
    search_fields = ("name", "address", "email")
    readonly_fields = ("created_at", "updated_at", "created_by")

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ("number", "tower_label", "residential_unit", "floor")
    list_filter = ("residential_unit", "tower_label")
    search_fields = ("number", "tower_label", "residential_unit__name")
    readonly_fields = ("qr_token", "qr_code", "created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": ("residential_unit", "number", "tower_label", "floor"),
            },
        ),
        (
            _("QR Information"),
            {
                "fields": ("qr_token", "qr_code"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ("user", "house", "is_owner", "approved", "relationship")
    list_filter = ("is_owner", "approved", "house__residential_unit")
    search_fields = ("user__email", "user__name", "house__number")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": ("house", "user", "is_owner", "relationship"),
            },
        ),
        (
            _("Approval Information"),
            {
                "fields": ("approved", "approved_by"),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
