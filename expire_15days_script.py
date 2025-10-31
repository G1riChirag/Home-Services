# Step 1: Open the Django shell
# python manage.py shell

# Step 2: Backdate one contact and one alert so they look older than 15 days:
from datetime import timedelta
from django.utils import timezone
from bookings.models import ContactEvent, ExposureAlert

now = timezone.now()
old_time = now - timedelta(days=16)

# Backdate the newest ContactEvent
ce = ContactEvent.objects.order_by('-id').first()
if ce:
    ce.occurred_at = old_time
    ce.save(update_fields=['occurred_at'])

# Backdate the newest ExposureAlert so it's expired long ago
ea = ExposureAlert.objects.order_by('-id').first()
if ea:
    ea.expires_at = old_time
    ea.save(update_fields=['expires_at'])

print('Before purge:', ContactEvent.objects.count(), 'contacts,', ExposureAlert.objects.count(), 'alerts')
exit()

# Step 3: Run the purge command
# python manage.py purge_privacy