import uuid
from io import BytesIO

import qrcode
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Choices for ResidentialUnit
PROPERTY_TYPE_CHOICES = (
    ("casa", "Casa"),
    ("apartamento", "Apartamento"),
)

STATUS_CHOICES = (
    ("pending", "Pendiente"),
    ("approved", "Aprobado"),
    ("rejected", "Rechazado"),
)


class TimeStampedModel(models.Model):
    """Abstract model for timestamping"""

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        abstract = True


class ResidentialUnit(TimeStampedModel):
    # Basic fields
    name = models.CharField(_("Name"), max_length=255)
    address = models.CharField(_("Address"), max_length=255)
    photo = models.ImageField(
        _("Photo"),
        upload_to="residential_units/photos/",
        blank=True,
    )
    map_url = models.URLField(_("Google Maps URL"))
    property_type = models.CharField(
        _("Property Type"),
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES,
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # Administrative fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_residential_units",
        verbose_name=_("Created By"),
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_residential_units",
        verbose_name=_("Approved By"),
    )

    # Additional fields
    phone = models.CharField(_("Contact Phone"), max_length=20, blank=True)
    email = models.EmailField(_("Contact Email"), blank=True)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Residential Unit")
        verbose_name_plural = _("Residential Units")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class House(TimeStampedModel):
    # Replace Tower with ResidentialUnit relation
    residential_unit = models.ForeignKey(
        ResidentialUnit,
        related_name="houses",
        on_delete=models.CASCADE,
        verbose_name=_("Residential Unit"),
    )
    tower_label = models.CharField(
        _("Tower"),
        max_length=50,
        blank=True,
        default="",
        help_text=_("Optional tower identifier if applicable"),
    )
    number = models.CharField(_("House/Apartment Number"), max_length=20)
    floor = models.PositiveSmallIntegerField(
        _("Floor"),
        null=True,
        blank=True,
        help_text=_("Optional floor if applicable"),
    )

    # Auto-generated QR field
    qr_token = models.UUIDField(
        _("QR Token"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    qr_code = models.ImageField(
        _("QR Code"),
        upload_to="residential_units/qr_codes/",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("House/Apartment")
        verbose_name_plural = _("Houses/Apartments")
        ordering = ["residential_unit", "tower_label", "number"]
        unique_together = ["residential_unit", "tower_label", "number"]

    def __str__(self):
        tower_info = f" - {self.tower_label}" if self.tower_label else ""
        return f"{self.number}{tower_info} - {self.residential_unit.name}"

    def generate_qr_code(self):
        """Generate QR code image with the house token"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(self.qr_token))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer)

        # Create a file to save to the ImageField
        filename = f"qr_code_{self.qr_token}.png"
        filebuffer = InMemoryUploadedFile(
            buffer,
            None,
            filename,
            "image/png",
            buffer.getbuffer().nbytes,
            None,
        )

        self.qr_code.save(filename, filebuffer, save=False)


class Resident(TimeStampedModel):
    house = models.ForeignKey(
        House,
        related_name="residents",
        on_delete=models.CASCADE,
        verbose_name=_("House/Apartment"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="residences",
        verbose_name=_("User"),
    )
    approved = models.BooleanField(_("Approved"), default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_residents",
        verbose_name=_("Approved By"),
    )
    is_owner = models.BooleanField(_("Is Owner"), default=False)
    relationship = models.CharField(
        _("Relationship"),
        max_length=100,
        blank=True,
        help_text=_("Family relationship if not owner"),
    )

    class Meta:
        verbose_name = _("Resident")
        verbose_name_plural = _("Residents")
        unique_together = ["house", "user"]

    def __str__(self):
        return f"{self.user.name} - {self.house.number}"

    def save(self, *args, **kwargs):
        # Auto-approve if created by staff or admin
        if not self.pk and self.user.role in ["staff", "admin"]:
            self.approved = True
            self.approved_by = self.user

        super().save(*args, **kwargs)


# Signal to generate QR code when a house is created
@receiver(post_save, sender=House)
def create_qr_code(sender, instance, created, **kwargs):
    if created and not instance.qr_code:
        instance.generate_qr_code()
        instance.save(update_fields=["qr_code"])
