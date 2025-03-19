import logging

from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import WhatsAppWebhookData
from .serializers import WhatsAppWebhookDataSerializer
from .tasks import process_whatsapp_message

logger = logging.getLogger(__name__)


class EventWebhookViewSet(viewsets.ModelViewSet):
    queryset = WhatsAppWebhookData.objects.all()
    serializer_class = WhatsAppWebhookDataSerializer


@method_decorator(csrf_exempt, name="dispatch")
class WebhookViewSet(viewsets.ViewSet):
    authentication_classes = []  # Deshabilitar autenticación
    permission_classes = [AllowAny]  # Permitir acceso a todos

    def create(self, request, *args, **kwargs):
        try:
            # Iniciar tarea asíncrona
            task = process_whatsapp_message.delay(request.data)
            logger.info("WhatsApp webhook task created: %s", task.id)
            return HttpResponse(status=200)
        except (ValueError, TypeError):
            logger.exception("Error processing webhook")
            return HttpResponse(status=200)  # Siempre devolver 200 a WhatsApp

    def list(self, request, *args, **kwargs):
        try:
            hub_mode = request.query_params.get("hub.mode")
            hub_token = request.query_params.get("hub.verify_token")
            hub_challenge = request.query_params.get("hub.challenge")

            if hub_mode == "subscribe" and hub_token == settings.WHATSAPP_VERIFY_TOKEN:
                logger.info("WhatsApp webhook verified successfully")
                return HttpResponse(hub_challenge, content_type="text/plain")
            logger.warning("Invalid verification token received")
            return JsonResponse(
                {"status": "error", "message": "Invalid token"},
                status=400,
            )
        except (KeyError, AttributeError):
            logger.exception("Error in webhook verification")
            return JsonResponse("", status=500)
