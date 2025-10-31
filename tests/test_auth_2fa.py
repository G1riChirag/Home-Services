import pyotp
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from profiles.models import UserProfile

@pytest.mark.django_db
def test_login_without_2fa_allows_password(client, django_user_model):
    user = django_user_model.objects.create_user(username="u1", password="pass12345")
    resp = client.post(reverse("users:login"), {"username": "u1", "password": "pass12345"})
    assert resp.status_code in (302, 200)  # Django LoginView redirects by default
    assert resp.wsgi_request.user.is_authenticated

@pytest.mark.django_db
def test_login_with_2fa_requires_otp(client, django_user_model):
    user = django_user_model.objects.create_user(username="u2", password="pass12345")
    prof, _ = UserProfile.objects.get_or_create(user=user)
    prof.totp_secret = pyotp.random_base32()
    prof.totp_enabled = True
    prof.save()

    # First submit: missing OTP -> should re-render with OTP modal
    resp = client.post(reverse("users:login"), {"username": "u2", "password": "pass12345"})
    assert resp.status_code == 200
    assert b"Two-Factor Code" in resp.content

    # Wrong OTP
    resp = client.post(reverse("users:login"),
        {"username":"u2","password":"pass12345","otp":"000000"})
    assert resp.status_code == 200
    assert b"Invalid or expired two-factor code" in resp.content

    # Correct OTP
    otp = pyotp.TOTP(prof.totp_secret).now()
    resp = client.post(reverse("users:login"),
        {"username":"u2","password":"pass12345","otp":otp})
    assert resp.status_code in (302, 200)
