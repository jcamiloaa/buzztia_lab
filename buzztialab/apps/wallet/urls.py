from django.urls import path

from . import views

app_name = "wallet"
urlpatterns = [
    path("", views.WalletDashboardView.as_view(), name="dashboard"),
    path("transactions/", views.transaction_history, name="transactions"),
    path(
        "transactions/export/",
        views.export_transactions_csv,
        name="export_transactions_csv",
    ),
    path("buy-credits/", views.buy_credits, name="buy_credits"),
    path(
        "send-verification/",
        views.send_verification_code,
        name="send_verification_code",
    ),
    path("verify-code/", views.verify_code, name="verify_code"),
]
