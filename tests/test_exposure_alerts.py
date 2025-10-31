import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from bookings.models import Booking, ContactEvent, ExposureAlert

@pytest.mark.django_db
def test_exposure_alerts_only_for_recent_contacts(client, django_user_model):
    u1 = django_user_model.objects.create_user(username="p1", password="x")
    u2 = django_user_model.objects.create_user(username="p2", password="x")

    # Log in as p2 to create a booking & check-in (simplified direct DB create here)
    b = Booking.objects.create(user=u1, type="General", status="Pending")
    # Recent contact
    ContactEvent.objects.create(user_a=u1, user_b=u2, occurred_at=timezone.now())
    # Old contact (> 15 days)
    ContactEvent.objects.create(user_a=u1, user_b=u2, occurred_at=timezone.now() - timedelta(days=20))

    client.force_login(u1)
    resp = client.post(reverse("report-positive"))
    assert resp.status_code in (302, 200)

    now = timezone.now()
    alerts = ExposureAlert.objects.filter(user=u2, acknowledged_at__isnull=True, expires_at__gt=now)
    assert alerts.count() == 1
