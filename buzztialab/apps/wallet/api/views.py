from django.utils.crypto import get_random_string
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from buzztialab.apps.wallet.api.serializers import WalletSerializer
from buzztialab.apps.wallet.models import Transaction
from buzztialab.apps.wallet.models import Wallet

# Error messages
AMOUNT_MUST_BE_POSITIVE = "Amount must be positive"
CREDITS_MUST_BE_POSITIVE = "Credits must be positive"


def _validate_positive_amount(amount_value):
    if amount_value <= 0:
        raise ValueError(AMOUNT_MUST_BE_POSITIVE)


def _validate_positive_credits(credit_value):
    if credit_value <= 0:
        raise ValueError(CREDITS_MUST_BE_POSITIVE)


class WalletViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def deposit(self, request, pk=None):
        wallet = self.get_object()
        amount = request.data.get("amount")
        try:
            amount = float(amount)
            _validate_positive_amount(amount)

            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=Transaction.TransactionType.DEPOSIT,
                description="PSE Deposit",
            )

            return Response(
                {
                    "status": "success",
                    "transaction_id": transaction.id,
                },
            )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def purchase_credits(self, request, pk=None):
        wallet = self.get_object()
        credit_amount = request.data.get("credits")
        payment_amount = request.data.get("amount")  # amount in local currency

        try:
            credit_value = float(credit_amount)
            payment_value = float(payment_amount)
            _validate_positive_credits(credit_value)
            _validate_positive_amount(payment_value)

            transaction = Transaction.objects.create(
                wallet=wallet,
                credits=credit_value,
                local_currency_amount=payment_value,
                transaction_type=Transaction.TransactionType.CREDIT_PURCHASE,
                reference_id=get_random_string(32),
                description=f"Purchase of {credit_value} credits",
            )

            return Response(
                {
                    "status": "success",
                    "transaction_id": transaction.id,
                    "reference_id": transaction.reference_id,
                },
            )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount or credits value"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def use_credits(self, request, pk=None):
        wallet = self.get_object()
        credit_amount = request.data.get("credits")
        description = request.data.get("description", "Service payment")

        try:
            credit_value = float(credit_amount)
            _validate_positive_credits(credit_value)

            if wallet.credits < credit_value:
                return Response(
                    {"error": "Insufficient credits"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            transaction = Transaction.objects.create(
                wallet=wallet,
                credits=credit_value,
                transaction_type=Transaction.TransactionType.SERVICE_PAYMENT,
                reference_id=get_random_string(32),
                description=description,
            )

            # Update wallet credits
            wallet.credits -= credit_value
            wallet.save()

            return Response(
                {
                    "status": "success",
                    "transaction_id": transaction.id,
                    "remaining_credits": wallet.credits,
                },
            )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid credits value"},
                status=status.HTTP_400_BAD_REQUEST,
            )
