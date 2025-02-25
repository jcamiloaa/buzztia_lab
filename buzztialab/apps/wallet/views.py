import csv
import json
import secrets
import string
from datetime import timedelta
from decimal import Decimal
from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from buzztialab.apps.wallet.models import Transaction
from buzztialab.apps.wallet.models import VerificationCode
from buzztialab.apps.wallet.models import Wallet


class WalletDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "wallet/index-wallet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)

        # Definir paquetes de créditos disponibles
        context["credit_packages"] = [
            {"credits": 100, "price": 10},
            {"credits": 500, "price": 45},
            {"credits": 1000, "price": 90},
            {"credits": 2000, "price": 170},
        ]

        # Obtener estadísticas de uso de créditos
        context["total_purchased"] = wallet.transactions.filter(
            transaction_type=Transaction.TransactionType.CREDIT_PURCHASE,
            status=Transaction.TransactionStatus.COMPLETED,
        ).count()

        context["total_spent"] = wallet.transactions.filter(
            transaction_type=Transaction.TransactionType.SERVICE_PAYMENT,
            status=Transaction.TransactionStatus.COMPLETED,
        ).count()

        # Obtener datos para el gráfico de los últimos 6 meses
        end_date = timezone.now()
        start_date = end_date - timedelta(days=180)  # 6 meses atrás

        monthly_stats = (
            wallet.transactions.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                status=Transaction.TransactionStatus.COMPLETED,
            )
            .annotate(
                month=TruncMonth("created_at"),
            )
            .values("month")
            .annotate(
                total_credits=Sum("credits"),
            )
            .order_by("month")
        )

        # Preparar datos para el gráfico
        chart_data = {
            "labels": [],
            "credits": [],
        }

        for stat in monthly_stats:
            chart_data["labels"].append(stat["month"].strftime("%b %Y"))
            chart_data["credits"].append(float(stat["total_credits"] or 0))

        context["chart_data"] = chart_data

        context["wallet"] = wallet
        context["recent_transactions"] = wallet.transactions.order_by("-created_at")[:5]
        return context


@login_required
def transaction_history(request):
    wallet = Wallet.objects.get(user=request.user)
    transactions = wallet.transactions.all()

    # Apply filters if present
    transaction_type = request.GET.get("type")
    status = request.GET.get("status")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if status:
        transactions = transactions.filter(status=status)
    if date_from:
        transactions = transactions.filter(created_at__gte=date_from)
    if date_to:
        transactions = transactions.filter(created_at__lte=date_to)

    # Calculate total sum of credits with formatting
    total_purchases = "{:,.0f}".format(
        wallet.transactions.filter(
            transaction_type="BUY",
            status="COM",
        ).aggregate(total=Sum("credits"))["total"]
        or 0,
    )

    total_payments = "{:,.0f}".format(
        wallet.transactions.filter(
            transaction_type="PAY",
            status="COM",
        ).aggregate(total=Sum("credits"))["total"]
        or 0,
    )

    total_savings = "{:,.0f}".format(
        wallet.transactions.filter(
            transaction_type="SAV",
            status="COM",
        ).aggregate(total=Sum("credits"))["total"]
        or 0,
    )

    total_refunds = "{:,.0f}".format(
        wallet.transactions.filter(
            transaction_type="REF",
            status="COM",
        ).aggregate(total=Sum("credits"))["total"]
        or 0,
    )

    transactions = transactions.order_by("-created_at")

    # Paginación
    page = request.GET.get("page", 1)
    paginator = Paginator(transactions, 10)  # 10 registros por página

    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    return render(
        request,
        "wallet/transaction_history.html",
        {
            "transactions": transactions,
            "wallet": wallet,
            "total_purchases": total_purchases,
            "total_payments": total_payments,
            "total_savings": total_savings,
            "total_refunds": total_refunds,
        },
    )


@login_required
def export_transactions_csv(request):
    wallet = Wallet.objects.get(user=request.user)
    transactions = wallet.transactions.all()

    # Apply same filters as in transaction_history view
    transaction_type = request.GET.get("type")
    status = request.GET.get("status")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if status:
        transactions = transactions.filter(status=status)
    if date_from:
        transactions = transactions.filter(created_at__gte=date_from)
    if date_to:
        transactions = transactions.filter(created_at__lte=date_to)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["Reference ID", "Type", "Credits", "Amount", "Status", "Description", "Date"],
    )

    for transaction in transactions:
        writer.writerow(
            [
                transaction.reference_id,
                transaction.get_transaction_type_display(),
                transaction.credits,
                transaction.local_currency_amount,
                transaction.get_status_display(),
                transaction.description,
                transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ],
        )

    return response


@login_required
def buy_credits(request):
    wallet = Wallet.objects.get(user=request.user)

    context = {
        "wallet": wallet,
        "credit_packages": [
            {"credits": 100, "price": 10, "id": "pack_100"},
            {"credits": 500, "price": 45, "id": "pack_500"},
            {"credits": 1000, "price": 90, "id": "pack_1000"},
            {"credits": 2000, "price": 170, "id": "pack_2000"},
        ],
        "banks": [
            {"id": "bancolombia", "name": "Bancolombia"},
            {"id": "davivienda", "name": "Davivienda"},
            {"id": "bbva", "name": "BBVA"},
        ],
    }

    if request.method == "POST":
        credits_str = request.POST.get("credits")
        bank = request.POST.get("bank")
        try:
            credit_amount = float(credits_str)
        except (ValueError, TypeError):
            messages.error(request, "Invalid credit amount")
            return redirect("wallet:buy_credits")

        transaction = Transaction.objects.create(
            wallet=wallet,
            credits=credit_amount,
            local_currency_amount=credit_amount,  # 1 credit = 1 peso
            transaction_type=Transaction.TransactionType.CREDIT_PURCHASE,
            status=Transaction.TransactionStatus.COMPLETED,
            reference_id=get_random_string(32),
            description=f"Simulated purchase of {credit_amount} credits via {bank}",
        )
        wallet.credits += Decimal(credit_amount)
        wallet.save()
        messages.success(request, f"Successfully purchased {credit_amount} credits!")
        complete_purchase(request, transaction)
        return redirect("wallet:dashboard")

    return render(request, "wallet/buy_credits.html", context)


@login_required
def send_verification_code(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        credit_amount = data.get("credits", 0)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    # Generate secure random 5-digit code
    code = "".join(secrets.choice(string.digits) for _ in range(5))

    # Delete any existing unused codes for this user
    VerificationCode.objects.filter(
        user=request.user,
        is_used=False,
    ).delete()

    # Create new verification code
    verification = VerificationCode.objects.create(
        user=request.user,
        code=code,
        credits=credit_amount,
    )

    # Prepare email
    context = {
        "user": request.user,
        "code": code,
    }
    email_html = render_to_string("wallet/email/verification_code.html", context)

    # Send email
    try:
        send_mail(
            subject=_("Your Credit Purchase Verification Code"),
            message=_("Your verification code is: ") + code,
            from_email=None,
            recipient_list=[request.user.email],
            html_message=email_html,
        )
        messages.success(request, _("Verification code has been sent to your email"))
        return JsonResponse({"success": True})
    except SMTPException as e:
        verification.delete()
        messages.error(request, _("Error sending verification code"))
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def verify_code(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        code = data.get("code")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    # Check if code exists and is valid
    verification = VerificationCode.objects.filter(
        user=request.user,
        code=code,
        is_used=False,
        created_at__gte=timezone.now() - timedelta(minutes=15),
    ).first()

    if not verification:
        return JsonResponse(
            {
                "success": False,
                "message": _("Invalid verification code"),
            },
        )

    # Mark code as used
    verification.is_used = True
    verification.save()

    return JsonResponse(
        {
            "success": True,
            "message": _("Code verified successfully"),
        },
    )


def complete_purchase(request, transaction):
    # Send confirmation email
    context = {
        "user": request.user,
        "credits": transaction.credits,
        "amount": transaction.local_currency_amount,
        "date": timezone.localtime(transaction.created_at).strftime(
            "%Y-%m-%d %H:%M:%S",
        ),
        "payment_method": transaction.description.split(" via ")[-1],
    }

    html_message = render_to_string("wallet/email/purchase_confirmation.html", context)

    send_mail(
        subject=_("Purchase Confirmation - BuzztiaLab"),
        message=_("Your credit purchase has been completed successfully."),
        from_email=None,
        recipient_list=[request.user.email],
        html_message=html_message,
    )
