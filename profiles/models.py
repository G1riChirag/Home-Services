from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=120, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    language = models.CharField(max_length=64, blank=True)
    citizenship = models.CharField(max_length=64, blank=True)

    # Overall vaccination boolean (derived by save(); do not toggle directly in UI)
    covid_vaccinated = models.BooleanField(null=True, blank=True)

    # Free-form/legacy consent JSON (kept for backward compatibility / analytics)
    consent = models.JSONField(default=dict, blank=True)

    # Structured address (JSON for minimal collection)
    address = models.JSONField(null=True, blank=True)

    # Granular consents
    consent_marketing = models.BooleanField(default=False)
    consent_healthdata = models.BooleanField(default=False)
    consent_updated_at = models.DateTimeField(null=True, blank=True)
    consent_version = models.CharField(max_length=20, blank=True, default="v1")

    # 2FA
    totp_secret = models.CharField(max_length=64, blank=True, default="")
    totp_enabled = models.BooleanField(default=False)

    # Vaccination proof (PDF only) + metadata
    vaccination_proof = models.FileField(
        upload_to="vaccination/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        help_text="Upload your COVID vaccination certificate (PDF only).",
    )
    vaccination_uploaded_at = models.DateTimeField(null=True, blank=True)
    vaccination_verified = models.BooleanField(
        default=False,
        help_text="Set by staff after manual review of the uploaded certificate.",
    )

    def __str__(self) -> str:
        return f"UserProfile({self.user.username})"

    def set_consents(self, marketing: bool, health: bool, version: str = "v1"):
        self.consent_marketing = marketing
        self.consent_healthdata = health
        self.consent_updated_at = timezone.now()
        self.consent_version = version

    # ---- Vaccination helpers ----
    def _sync_vax_boolean(self):
        """
        Keep covid_vaccinated consistent with proof + verification:
          - Verified proof -> True
          - Proof present but not verified -> None (unknown / pending)
          - No proof -> False
        """
        if self.vaccination_verified:
            self.covid_vaccinated = True
        elif self.vaccination_proof:
            self.covid_vaccinated = None
        else:
            self.covid_vaccinated = False

    @property
    def vaccination_status(self) -> str:
        """Convenient display string for templates/admin."""
        if self.vaccination_verified:
            return "Verified"
        if self.vaccination_proof:
            return "Awaiting verification"
        return "Not provided"

    def save(self, *args, **kwargs):
        # keep the boolean aligned with current proof + verified flag
        self._sync_vax_boolean()
        super().save(*args, **kwargs)
