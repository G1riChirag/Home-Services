import io
import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
def test_registration_rejects_non_pdf(client):
    data = {
        "username": "alice",
        "password1": "Strongpass123!",
        "password2": "Strongpass123!",
    }
    f = SimpleUploadedFile("not.pdf", b"hello", content_type="text/plain")
    data["vaccination_proof"] = f
    resp = client.post(reverse("users:register"), data)
    assert resp.status_code == 200
    assert b"PDF required" in resp.content

@pytest.mark.django_db
def test_registration_accepts_small_pdf(client):
    data = {
        "username": "bob",
        "password1": "Strongpass123!",
        "password2": "Strongpass123!",
    }
    f = SimpleUploadedFile("ok.pdf", b"%PDF-1.4\n...", content_type="application/pdf")
    data["vaccination_proof"] = f
    resp = client.post(reverse("users:register"), data)
    # Register redirects to login on success
    assert resp.status_code in (302, 200)
