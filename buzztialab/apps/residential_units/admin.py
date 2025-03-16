from django.contrib import admin

from .models import House
from .models import Resident
from .models import ResidentialUnit


@admin.register(ResidentialUnit)
class ResidentialUnitAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address",
        "property_type",
        "status",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = ("property_type", "status", "is_active", "created_at")
    search_fields = ("name", "address", "description")
    readonly_fields = ("created_at", "updated_at", "created_by")

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ("number", "tower_label", "residential_unit", "floor")
    list_filter = ("residential_unit", "floor")
    search_fields = ("number", "tower_label", "residential_unit__name")
    readonly_fields = ("qr_token", "qr_code", "created_at", "updated_at")


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ("user", "house", "is_owner", "approved", "approved_by")
    list_filter = ("is_owner", "approved", "created_at")
    search_fields = ("user__email", "house__number", "relationship")
    readonly_fields = ("created_at", "updated_at")
