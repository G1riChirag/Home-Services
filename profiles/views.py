import base64
from io import BytesIO
import pyotp
import qrcode

from django.contrib import messages
from django.conf import settings
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy, reverse
from django.db import models  # for models.Q in ReportPositiveView

from .models import UserProfile
from .forms import UserProfileForm
from utils.mixins import BreadcrumbsMixin

# --- NEW imports for health/exposure features ---
from django.utils import timezone
from datetime import timedelta
from bookings.models import ContactEvent, ExposureAlert
# ------------------------------------------------


def _qr_base64_for(secret: str, user, issuer: str) -> str:
    """Build otpauth URI and return a base64 PNG QR code."""
    uri = pyotp.TOTP(secret).provisioning_uri(
        name=user.email or user.username, issuer_name=issuer
    )
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


class ProfileView(LoginRequiredMixin, BreadcrumbsMixin, DetailView):
    model = UserProfile
    template_name = "profiles/profile.html"
    context_object_name = "profile"

    def get_object(self):
        obj, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile: UserProfile = self.object
        if not profile.totp_secret:
            profile.totp_secret = pyotp.random_base32()
            profile.save(update_fields=["totp_secret"])

        ctx["breadcrumbs"] = [
            {"label": "Home", "url": reverse("home")},
            {"label": "Profile"},
        ]
        issuer = getattr(settings, "SITE_NAME", "HomeServices")
        ctx["twofa_enabled"] = bool(profile.totp_enabled)
        ctx["twofa_secret"] = profile.totp_secret
        ctx["twofa_qr_base64"] = _qr_base64_for(
            profile.totp_secret, self.request.user, issuer
        )
        return ctx


class Profile2FAEnableView(LoginRequiredMixin, View):
    def post(self, request):
        otp = request.POST.get("otp", "")
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        # Ensure a secret exists
        if not profile.totp_secret:
            profile.totp_secret = pyotp.random_base32()
            profile.save(update_fields=["totp_secret"])

        if pyotp.TOTP(profile.totp_secret).verify(otp, valid_window=1):
            if not profile.totp_enabled:
                profile.totp_enabled = True
                profile.save(update_fields=["totp_enabled"])
            messages.success(request, "Two-Factor Authentication enabled.")
        else:
            messages.error(request, "Invalid or expired code. Please try again.")

        return redirect("profile")


class Profile2FADisableView(LoginRequiredMixin, View):
    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.totp_enabled = False
        # Optional: rotate/clear secret so re-enable requires re-scan
        # profile.totp_secret = ""
        profile.save(update_fields=["totp_enabled"])  # or ["totp_enabled", "totp_secret"]
        messages.info(request, "Two-Factor Authentication disabled.")
        return redirect("profile")


class ProfileUpdateView(LoginRequiredMixin, BreadcrumbsMixin, UpdateView):
    template_name = "profiles/profile_form.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("profile")

    def get_object(self):
        obj, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["breadcrumbs"] = [
            {"label": "Home", "url": reverse("home")},
            {"label": "Profile", "url": reverse("profile")},
            {"label": "Edit Profile"},
        ]
        return ctx


# =========================
# Health / Exposure Views
# =========================

class ReportPositiveView(LoginRequiredMixin, View):
    """
    Confirmable action: On POST, find contacts in the last 15 days and create alerts for them.
    Reporter identity is never revealed in any user-visible alert/banner.
    """
    def get(self, request):
        # Simple confirm flow; replace with a confirm template if preferred.
        messages.warning(
            request,
            "Confirm you want to anonymously notify your recent contacts (last 15 days)."
        )
        return redirect("profile")

    def post(self, request):
        user = request.user
        now = timezone.now()
        cutoff = now - timedelta(days=15)

        # Find all contact events in the window involving the reporter
        qs = ContactEvent.objects.filter(occurred_at__gte=cutoff).filter(
            models.Q(user_a=user) | models.Q(user_b=user)
        )

        # Distinct other users
        other_ids = set()
        for c in qs.only("user_a_id", "user_b_id"):
            other_ids.add(c.user_a_id if c.user_b_id == user.id else c.user_b_id)
        other_ids.discard(user.id)

        # Create alerts for each
        expires = now + timedelta(days=15)
        created = 0
        for uid in other_ids:
            ExposureAlert.objects.create(
                user_id=uid,
                created_at=now,
                expires_at=expires,
                source_reported_at=now,
            )
            created += 1

        messages.success(
            request,
            f"Anonymous exposure alerts sent to {created} contact(s). Thank you for reporting."
        )
        return redirect("profile")


class AcknowledgeAlertView(LoginRequiredMixin, View):
    """Mark all active alerts for the user as acknowledged (dismiss banner)."""
    def post(self, request):
        now = timezone.now()
        qs = ExposureAlert.objects.filter(
            user=request.user,
            acknowledged_at__isnull=True,
            expires_at__gt=now,
        )
        count = qs.update(acknowledged_at=now)
        if count:
            messages.success(request, "Exposure warning dismissed.")
        return redirect("home")
