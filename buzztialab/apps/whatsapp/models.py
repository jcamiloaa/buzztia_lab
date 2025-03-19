import logging

from django.db import models

logger = logging.getLogger(__name__)


class WhatsAppWebhookData(models.Model):
    DIRECTION_CHOICES = [
        ("inbound", "Mensaje Entrante"),
        ("outbound", "Mensaje Saliente"),
    ]

    STATUS_CHOICES = [
        ("new", "Nuevo"),
        ("pending", "Pendiente"),
        ("in_progress", "En Proceso"),
        ("completed", "Completado"),
        ("failed", "Fallido"),
        ("ignored", "Ignorado"),
    ]

    ACTION_CHOICES = [
        ("none", "Sin Acción"),
        ("menu", "Mostrar Menú"),
        ("support", "Soporte"),
        ("payment", "Pago"),
        ("info", "Información"),
        ("custom", "Personalizado"),
    ]

    # Campos existentes
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Nuevos campos para identificación
    wa_id = models.CharField(
        max_length=20,
        blank=True,
        help_text="WhatsApp ID del contacto",
    )
    contact_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nombre del contacto",
    )
    message_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID del mensaje",
    )
    message_type = models.CharField(
        max_length=20,
        blank=True,
        help_text="Tipo de mensaje",
    )
    message_text = models.TextField(blank=True, help_text="Contenido del mensaje")
    timestamp = models.CharField(
        max_length=20,
        blank=True,
        help_text="Timestamp del mensaje",
    )
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        default="inbound",
        help_text="Dirección del mensaje (entrante/saliente)",
    )

    # Nuevos campos para gestión de conversaciones
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        help_text="Estado actual del mensaje",
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        default="none",
        help_text="Acción requerida/tomada",
    )
    action_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Datos adicionales para la acción",
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Cuando se procesó el mensaje",
    )
    conversation_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID de la conversación",
    )
    parent_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="responses",
        help_text="Mensaje al que responde",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "WhatsApp Message"
        verbose_name_plural = "WhatsApp Messages"

    def __str__(self):
        return f"{self.contact_name} ({self.wa_id}) - {self.created_at}"

    def save(self, *args, **kwargs):
        if self.data:
            try:
                entry = self.data.get("entry", [{}])[0]
                changes = entry.get("changes", [{}])[0]
                value = changes.get("value", {})

                self._extract_contact_info(value)
                self._extract_message_info(value)
                self._determine_direction(value)
                self._handle_conversation(value)

            except (KeyError, IndexError):
                logger.exception("Error processing webhook data")

        super().save(*args, **kwargs)

    def _extract_contact_info(self, value):
        """Extract contact information from webhook data."""
        contacts = value.get("contacts", [{}])
        if contacts:
            self.wa_id = contacts[0].get("wa_id", "")
            self.contact_name = contacts[0].get("profile", {}).get("name", "")

    def _extract_message_info(self, value):
        """Extract message information from webhook data."""
        messages = value.get("messages", [{}])
        if messages:
            message = messages[0]
            self.message_id = message.get("id", "")
            self.message_type = message.get("type", "")
            self.timestamp = message.get("timestamp", "")
            if message.get("type") == "text":
                self.message_text = message.get("text", {}).get("body", "")

    def _determine_direction(self, value):
        """Determine message direction based on webhook data."""
        messages = value.get("messages", [])
        statuses = value.get("statuses", [])
        self.direction = (
            "inbound" if messages else "outbound" if statuses else self.direction
        )

    def _handle_conversation(self, value):
        """Handle conversation ID and parent message."""
        if not self.conversation_id:
            self.conversation_id = f"{self.wa_id}_{self.timestamp}"

        if value.get("context"):
            parent_id = value.get("context", {}).get("id")
            if parent_id:
                try:
                    parent = WhatsAppWebhookData.objects.filter(
                        message_id=parent_id,
                    ).first()
                    if parent:
                        self.parent_message = parent
                        self.conversation_id = parent.conversation_id
                except (
                    WhatsAppWebhookData.DoesNotExist,
                    WhatsAppWebhookData.MultipleObjectsReturned,
                ):
                    logger.exception("Error linking parent message")
