import uuid
from dataclasses import dataclass
from typing import Optional
from django.conf import settings
from .models import Payment


@dataclass
class ProviderResult:
    intent_id: str
    charge_id: Optional[str] = None
    status: str = Payment.Status.REQUIRES_ACTION
    error_code: str = ""


class SandboxProvider:
    """
    Dev-only provider: instantly "succeeds" without collecting cards.
    Swap with real Stripe/PayPal adapters later.
    """
    name = "sandbox"

    def create_intent(self, payment: Payment) -> ProviderResult:
        iid = f"sbox_intent_{uuid.uuid4().hex[:16]}"
        # For DEBUG we can mark as succeeded immediately.
        return ProviderResult(intent_id=iid, status=Payment.Status.SUCCEEDED, charge_id=f"sbox_charge_{uuid.uuid4().hex[:16]}")

    def fetch_status(self, payment: Payment) -> ProviderResult:
        # In Sandbox, intent succeeds immediately.
        return ProviderResult(
            intent_id=payment.provider_intent_id or f"sbox_intent_{uuid.uuid4().hex[:16]}",
            charge_id=payment.provider_charge_id or f"sbox_charge_{uuid.uuid4().hex[:16]}",
            status=Payment.Status.SUCCEEDED,
        )


def get_provider(name: str):
    # Later: return StripeProvider(), PaypalProvider() etc.
    return SandboxProvider()
