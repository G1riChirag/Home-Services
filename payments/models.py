from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from bookings.models import Booking


class Payment(models.Model):
    class Status(models.TextChoices):
        REQUIRES_ACTION = "requires_action"
        PROCESSING = "processing"
        SUCCEEDED = "succeeded"
        FAILED = "failed"
        REFUNDED = "refunded"
        CANCELED = "canceled"

    PROVIDER_CHOICES = [
        ("sandbox", "Sandbox"),
        ("stripe", "Stripe"),
        ("paypal", "PayPal"),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="sandbox")

    # Money
    amount_cents = models.IntegerField()
    currency = models.CharField(max_length=8, default="AUD")

    # Provider refs (never store card data)
    provider_intent_id = models.CharField(max_length=120, blank=True, default="")
    provider_charge_id = models.CharField(max_length=120, blank=True, default="")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUIRES_ACTION)
    error_code = models.CharField(max_length=64, blank=True, default="")

    # bookkeeping
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["booking", "status"]),
            models.Index(fields=["provider", "provider_intent_id"]),
        ]

    def __str__(self):
        return f"Payment(b#{self.booking_id} {self.amount_cents/100:.2f} {self.currency} {self.status})"


class Invoice(models.Model):
    """
    Minimal, immutable snapshot for a payment (or set of payments).
    Keep it simple: one invoice per successful full payment for now.
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="invoices")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")

    number = models.CharField(max_length=40, unique=True)
    issued_at = models.DateTimeField(default=timezone.now)

    # Snapshot values so invoices don’t change retroactively
    currency = models.CharField(max_length=8, default="AUD")
    subtotal_cents = models.IntegerField(default=0)
    tax_cents = models.IntegerField(default=0)
    total_cents = models.IntegerField(default=0)

    # Optional freeform snapshot (e.g., lines or meta)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"Invoice {self.number} — b#{self.booking_id} ${self.total_cents/100:.2f}"
