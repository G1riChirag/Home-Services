# bookings/management/commands/purge_privacy.py
from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import ContactEvent, ExposureAlert


class Command(BaseCommand):
    help = (
        "Purge privacy-sensitive data:\n"
        "- ContactEvent older than retention window\n"
        "- ExposureAlert whose expiry is older than retention window"
    )

    def handle(self, *args, **options):
        days = getattr(settings, "PRIVACY_RETENTION_DAYS", 15)
        now = timezone.now()
        cutoff = now - timedelta(days=days)

        # 1) Delete ContactEvent older than retention window
        old_contacts = ContactEvent.objects.filter(occurred_at__lt=cutoff)
        contacts_count = old_contacts.count()
        old_contacts.delete()

        # 2) Delete ExposureAlert whose expiry is older than retention window
        old_alerts = ExposureAlert.objects.filter(expires_at__lt=cutoff)
        alerts_count = old_alerts.count()
        old_alerts.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Purged {contacts_count} ContactEvent(s) and {alerts_count} ExposureAlert(s). "
                f"(retention={days}d, cutoff={cutoff:%Y-%m-%d %H:%M:%S %Z})"
            )
        )
