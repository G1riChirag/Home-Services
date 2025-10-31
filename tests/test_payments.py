import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from bookings.models import Booking
from payments.models import Invoice

@pytest.mark.django_db
def test_payment_creates_single_invoice(client, django_user_model):
    u = django_user_model.objects.create_user(username="payer", password="x")
    b = Booking.objects.create(user=u, type="General", status="Pending", quoted_price_cents=12345)

    client.force_login(u)
    resp = client.post(reverse("payments:start", args=[b.id]))
    assert resp.status_code in (302, 200)
    assert Invoice.objects.filter(booking=b).count() == 1

    # Try paying again — must not create duplicates
    resp = client.post(reverse("payments:start", args=[b.id]))
    assert Invoice.objects.filter(booking=b).count() == 1
