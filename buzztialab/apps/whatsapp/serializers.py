from rest_framework import serializers

from .models import WhatsAppWebhookData


class WhatsAppWebhookDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppWebhookData
        fields = "__all__"
