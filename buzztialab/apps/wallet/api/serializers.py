from rest_framework import serializers

from buzztialab.apps.wallet.models import Transaction
from buzztialab.apps.wallet.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "credits", "created_at", "updated_at"]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display",
        read_only=True,
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "credits",
            "local_currency_amount",
            "transaction_type",
            "transaction_type_display",
            "status",
            "status_display",
            "reference_id",
            "description",
            "created_at",
        ]
        read_only_fields = fields
