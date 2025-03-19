import logging
from typing import Any

from celery import shared_task
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="whatsapp.process_whatsapp_message",
)
def process_whatsapp_message(self, payload: dict[str, Any]) -> bool:
    """
    Process incoming WhatsApp message webhook payload
    """
    try:
        logger.info("Processing WhatsApp message: %s", payload)

        # Extract entry and changes from payload
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]

        # Extract message details
        value = changes.get("value", {})
        messages = value.get("messages", [{}])

        for message in messages:
            # Process each message here
            message_type = message.get("type")
            if message_type == "text":
                text = message.get("text", {}).get("body", "")
                logger.info("Received text message: %s", text)
                # Add your text message handling logic here

            # Store message in database
            from .models import WhatsAppWebhookData

            WhatsAppWebhookData.objects.create(data=payload)
    except ValidationError as e:
        logger.exception("Validation error processing WhatsApp message")
        raise self.retry(exc=e) from e
    except Exception as e:
        logger.exception("Error processing WhatsApp message")
        raise self.retry(exc=e) from e
    else:
        return True
