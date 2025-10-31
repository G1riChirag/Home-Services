# bookings/management/commands/clear_expired_alerts.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bookings.models import ExposureAlert

class Command(BaseCommand):
    help = "Delete long-expired exposure alerts (older than 30 days past expiry)."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=30)
        qs = ExposureAlert.objects.filter(expires_at__lt=cutoff)
        deleted, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} expired alerts"))
