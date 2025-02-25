from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    credits = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Available Credits",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Credits"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        CREDIT_PURCHASE = "BUY", _("Credit Purchase")
        SERVICE_PAYMENT = "PAY", _("Service Payment")
        CREDIT_REFUND = "REF", _("Credit Refund")
        SAVINGS_CREDIT = "SAV", _("Savings Credit")

    class TransactionStatus(models.TextChoices):
        PENDING = "PEN", _("Pending")
        COMPLETED = "COM", _("Completed")
        FAILED = "FAI", _("Failed")

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    credits = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Credits Amount",
        default=0.00,  # Add default value
    )
    local_currency_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Amount in Local Currency",
        default=0.00,  # Add default value
    )
    transaction_type = models.CharField(max_length=3, choices=TransactionType.choices)
    status = models.CharField(
        max_length=3,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )
    reference_id = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.credits} credits"


class VerificationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=5)
    credits = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Verification code for {self.user.email}"
