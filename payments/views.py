from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum

from bookings.models import Booking
from .models import Payment, Invoice
from .services import get_provider


def _user_owns_booking(user, booking_id) -> Booking:
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.user_id != user.id:
        raise Http404()
    return booking


class StartPaymentView(LoginRequiredMixin, View):
    """
    Create (or resume) a Payment for the booking's quoted amount.
    Sandbox provider: immediately succeeds and confirms booking.
    """
    def post(self, request, booking_id):
        booking = _user_owns_booking(request.user, booking_id)
        if not booking.quoted_price_cents:
            messages.error(request, "This booking is not yet payable.")
            return redirect("booking-detail", pk=booking.id)

        # If fully paid already, short-circuit
        paid = booking.payments.filter(status=Payment.Status.SUCCEEDED).aggregate(total_cents_sum=Sum("amount_cents"))["total_cents_sum"] or 0
        if paid >= (booking.quoted_price_cents or 0):
            messages.info(request, "This booking is already fully paid.")
            return redirect("booking-detail", pk=booking.id)

        amount = (booking.quoted_price_cents or 0) - paid
        provider = get_provider("sandbox")

        with transaction.atomic():
            # Create a new Payment attempt
            p = Payment.objects.create(
                booking=booking,
                user=request.user,
                provider=provider.name,
                amount_cents=amount,
                currency="AUD",
                status=Payment.Status.REQUIRES_ACTION,
            )

            # Create intent at provider
            result = provider.create_intent(p)
            p.provider_intent_id = result.intent_id
            p.provider_charge_id = (result.charge_id or "")
            p.status = result.status
            p.error_code = result.error_code
            p.save()

            # If sandbox marked it succeeded immediately, finalize booking + invoice
            if p.status == Payment.Status.SUCCEEDED:
                _finalize_successful_payment(p)

        if p.status == Payment.Status.SUCCEEDED:
            messages.success(request, "Payment successful. Thank you!")
            return redirect("booking-detail", pk=booking.id)

        # For real providers: redirect to their hosted checkout
        messages.info(request, "Redirecting to checkout…")
        return redirect("booking-detail", pk=booking.id)


def _finalize_successful_payment(payment: Payment):
    """Idempotent booking + invoice post-processing for successful payments."""
    booking = payment.booking

    # If fully paid, mark booking Confirmed (if still Pending)
    total_paid = booking.payments.filter(status=Payment.Status.SUCCEEDED).aggregate(total_cents_sum=Sum("amount_cents"))["total_cents_sum"] or 0
    if total_paid >= (booking.quoted_price_cents or 0) and booking.status == "Pending":
        booking.status = "Confirmed"
        booking.save(update_fields=["status"])

    # If this payment results in full payment and no prior invoice, create one
    has_invoice = booking.invoices.exists()
    if not has_invoice and total_paid >= (booking.quoted_price_cents or 0):
        _create_invoice_for_booking(booking, total_paid)


def _create_invoice_for_booking(booking: Booking, total_cents: int) -> Invoice:
    """
    Minimal invoice: no GST/VAT math for now.
    If you add tax, compute and store snapshot here.
    """
    number = f"INV-{timezone.now().strftime('%Y%m%d')}-{booking.id}"
    return Invoice.objects.create(
        booking=booking,
        user=booking.user,
        number=number,
        issued_at=timezone.now(),
        currency="AUD",
        subtotal_cents=total_cents,
        tax_cents=0,
        total_cents=total_cents,
        meta={
            "booking_id": booking.id,
            "user": booking.user.username,
            "note": "Auto-generated on successful payment.",
        },
    )


class InvoiceDetailView(LoginRequiredMixin, View):
    def get(self, request, invoice_number):
        invoice = get_object_or_404(Invoice, number=invoice_number)
        if invoice.user_id != request.user.id:
            raise Http404()
        return render(request, "payments/invoice_detail.html", {"invoice": invoice})


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    """
    Placeholder for real provider webhooks.
    Keep it idempotent if you add real provider integration.
    """
    def post(self, request):
        return HttpResponse(status=200)
