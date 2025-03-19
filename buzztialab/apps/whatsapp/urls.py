from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EventWebhookViewSet
from .views import WebhookViewSet

app_name = "whatsapp"

router = DefaultRouter()
router.register(r"webhook", WebhookViewSet, basename="webhook")
router.register(r"events", EventWebhookViewSet, basename="events")

urlpatterns = [
    path("", include(router.urls)),
]
