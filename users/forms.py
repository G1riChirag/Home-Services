# users/forms.py
import pyotp
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UsernameField, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from profiles.models import UserProfile


class TwoFactorAuthenticationForm(forms.Form):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True, "class": "form-control"}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    otp = forms.RegexField(
        label=_("One-time code"),
        regex=r"^\d{6}$",
        required=False,
        error_messages={"invalid": _("Enter the 6-digit code.")},
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "inputmode": "numeric",
            "autocomplete": "one-time-code",
            "pattern": r"\d{6}",
            "maxlength": "6",
        }),
    )

    error_messages = {
        "invalid_login": _("Please enter a correct username and password."),
        "inactive": _("This account is inactive."),
        "otp_required": _("Two-factor code is required."),
        "otp_invalid": _("Invalid or expired two-factor code."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    # --- helper: get the profile no matter the related_name or existence
    @staticmethod
    def _get_profile(user):
        prof = getattr(user, "userprofile", None) or getattr(user, "profile", None)
        if prof:
            return prof
        # Fallback: query
        return UserProfile.objects.filter(user=user).first()

    def clean(self):
        cleaned = super().clean()
        username = (cleaned.get("username") or "").strip()
        password = cleaned.get("password")
        otp = (cleaned.get("otp") or "").strip()

        user = authenticate(self.request, username=username, password=password)
        if user is None:
            raise forms.ValidationError(self.error_messages["invalid_login"], code="invalid_login")
        if not user.is_active:
            raise forms.ValidationError(self.error_messages["inactive"], code="inactive")

        profile = self._get_profile(user)

        # If no profile or 2FA not enabled -> allow password-only login
        if not profile or not getattr(profile, "totp_enabled", False):
            self.user_cache = user
            return cleaned

        # 2FA enabled -> require a valid OTP
        if not otp:
            self._show_otp_modal = True
            self._otp_first_prompt = True        # <— first time we’re prompting for OTP
            self.add_error("otp", self.error_messages["otp_required"])
            return cleaned

        secret = getattr(profile, "totp_secret", "") or ""
        if not secret or not pyotp.TOTP(secret).verify(otp, valid_window=1):
            self._show_otp_modal = True
            # no _otp_first_prompt here — this is a real error after user tried
            self.add_error("otp", self.error_messages["otp_invalid"])
            return cleaned

        self.user_cache = user
        return cleaned

    def get_user(self):
        return self.user_cache


# --- Registration form that REQUIRES a PDF vaccination proof ---
class RegistrationForm(UserCreationForm):
    vaccination_proof = forms.FileField(
        required=True,
        help_text="Upload your COVID vaccination certificate (PDF only, max 2 MB)."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)  # add email later if desired

    def clean_vaccination_proof(self):
        f = self.cleaned_data.get("vaccination_proof")
        if not f:
            raise ValidationError("Vaccination proof is required.")

        # 2 MB size cap
        if getattr(f, "size", 0) > 2 * 1024 * 1024:
            raise ValidationError("File too large (max 2 MB).")

        # Basic MIME check (extension is also validated by model validators, but double-check here)
        ctype = getattr(f, "content_type", "") or ""
        if ctype not in ("application/pdf", "application/x-pdf"):
            raise ValidationError("PDF required.")

        return f

    def save(self, commit=True):
        user = super().save(commit=commit)
        # Ensure a profile exists
        prof, _ = UserProfile.objects.get_or_create(user=user)
        f = self.cleaned_data.get("vaccination_proof")
        if f:
            prof.vaccination_proof = f
            prof.vaccination_uploaded_at = timezone.now()
            if commit:
                prof.save()
        return user

# --- Delete Account form with password + optional OTP ---
class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Re-enter your password to confirm."
    )
    otp = forms.RegexField(           # will be optional unless 2FA is enabled
        label=_("One-time code"),
        regex=r"^\d{6}$",
        required=False,
        error_messages={"invalid": _("Enter the 6-digit code.")},
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "inputmode": "numeric",
            "autocomplete": "one-time-code",
            "pattern": r"\d{6}",
            "maxlength": "6",
        }),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = getattr(request, "user", None)
        # determine if OTP is required
        self.requires_otp = False
        if self.user and self.user.is_authenticated:
            prof = getattr(self.user, "userprofile", None) or getattr(self.user, "profile", None)
            if prof and getattr(prof, "totp_enabled", False):
                self.requires_otp = True
                # make field required dynamically
                self.fields["otp"].required = True

    def clean(self):
        cleaned = super().clean()
        if not self.user or not self.user.is_authenticated:
            raise ValidationError(_("Not authenticated."))

        # password check
        pwd = cleaned.get("password") or ""
        if not self.user.check_password(pwd):
            self.add_error("password", _("Incorrect password."))

        # otp check (if required)
        if self.requires_otp:
            secret = ""
            prof = getattr(self.user, "userprofile", None) or getattr(self.user, "profile", None)
            if prof:
                secret = getattr(prof, "totp_secret", "") or ""
            otp = (cleaned.get("otp") or "").strip()
            if not secret or not pyotp.TOTP(secret).verify(otp, valid_window=1):
                self.add_error("otp", _("Invalid or expired two-factor code."))

        # surface form-level errors if any field added errors
        if self.errors:
            raise ValidationError(_("Please correct the errors below and try again."))
        return cleaned
