from django.contrib import admin
from django.utils.html import format_html

from .models import WhatsAppWebhookData


@admin.register(WhatsAppWebhookData)
class WhatsAppWebhookDataAdmin(admin.ModelAdmin):
    list_display = (
        "contact_name",
        "wa_id",
        "message_text",
        "direction",
        "status",
        "action",
        "conversation_id",
        "created_at",
    )
    list_filter = (
        "direction",
        "status",
        "action",
        "message_type",
        "created_at",
    )
    search_fields = (
        "contact_name",
        "wa_id",
        "message_text",
        "conversation_id",
    )
    readonly_fields = (
        "created_at",
        "processed_at",
        "get_formatted_data",
        "conversation_id",
    )

    @admin.display(
        description="Raw Data",
    )
    def get_formatted_data(self, obj):
        """Returns formatted JSON data"""
        import json

        formatted_json = json.dumps(obj.data, indent=2)
        return format_html(
            '<pre style="background-color: #000000; color: #ffffff; padding: 15px; '
            "border-radius: 4px; white-space: pre-wrap; max-height: 500px; "
            'overflow-y: auto;">{}</pre>',
            formatted_json,
        )
