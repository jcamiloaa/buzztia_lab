from django.contrib import admin

from .models import Transaction
from .models import VerificationCode
from .models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ["user", "credits", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "User Information",
            {
                "fields": ("user",),
            },
        ),
        (
            "Credit Information",
            {
                "fields": ("credits",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "reference_id",
        "wallet",
        "credits",
        "local_currency_amount",
        "transaction_type",
        "status",
        "created_at",
    ]
    list_filter = [
        "transaction_type",
        "status",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "wallet__user__username",
        "wallet__user__email",
        "reference_id",
        "description",
    ]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Transaction Details",
            {
                "fields": (
                    "wallet",
                    "credits",
                    "local_currency_amount",
                    "transaction_type",
                    "status",
                    "reference_id",
                ),
            },
        ),
        (
            "Additional Information",
            {
                "fields": ("description",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "code",
        "credits",
        "is_used",
        "created_at",
    ]
    list_filter = [
        "is_used",
        "created_at",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "code",
    ]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "User Information",
            {
                "fields": ("user",),
            },
        ),
        (
            "Verification Details",
            {
                "fields": (
                    "code",
                    "credits",
                    "is_used",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    def has_change_permission(self, request, obj=None):
        # Prevent editing of verification codes for security
        return False
