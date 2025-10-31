from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from catalog.models import Service, ServicePackage


class Booking(models.Model):
    TYPE_CHOICES = [("General", "General"), ("Package", "Package"), ("Specific", "Specific")]
    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("InProgress", "InProgress"),
        ("Done", "Done"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="Draft")
    preferred_date = models.DateField(null=True, blank=True)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    quoted_price_cents = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    address = models.CharField(max_length=510, null=True, blank=True)
    package = models.ForeignKey(ServicePackage, null=True, blank=True, on_delete=models.SET_NULL)
    service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking({self.id}, {self.user.username}, {self.type}, {self.status})"

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="review")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range (1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review({self.booking.id}, {self.rating})"
    
    def get_service(self):
        return self.booking.service 

class ContactEvent(models.Model):
    """
    A pairwise contact between two users at a point in time.
    We always store (user_a_id < user_b_id) to avoid duplicates with reversed order.
    """
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts_as_a")
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts_as_b")
    occurred_at = models.DateTimeField(default=timezone.now)
    booking = models.ForeignKey("Booking", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=["occurred_at"]),
            models.Index(fields=["user_a", "occurred_at"]),
            models.Index(fields=["user_b", "occurred_at"]),
        ]
        constraints = [
            models.CheckConstraint(check=~models.Q(user_a=models.F("user_b")), name="no_self_contact"),
        ]

    def save(self, *args, **kwargs):
        # Normalize ordering so user_a.id < user_b.id
        if self.user_a_id and self.user_b_id and self.user_a_id > self.user_b_id:
            self.user_a_id, self.user_b_id = self.user_b_id, self.user_a_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Contact({self.user_a_id},{self.user_b_id}) @ {self.occurred_at:%Y-%m-%d %H:%M}"


# -------- Exposure alerts (with custom queryset/manager) -------- #

class ExposureAlertQuerySet(models.QuerySet):
    def active_for(self, user):
        """Active = not acknowledged and not expired, for a specific user."""
        now = timezone.now()
        return self.filter(user=user, acknowledged_at__isnull=True, expires_at__gt=now)

    def active(self):
        """All active alerts (for any user)."""
        now = timezone.now()
        return self.filter(acknowledged_at__isnull=True, expires_at__gt=now)


class ExposureAlert(models.Model):
    """
    An anonymized alert for a user that they were exposed, created
    when some other user reports a positive COVID test.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exposure_alerts")
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    # Optional: for audit; do not reveal reporter identity anywhere user-visible
    source_reported_at = models.DateTimeField(null=True, blank=True)

    # Managers
    objects = ExposureAlertQuerySet.as_manager()          # full queryset (with helpers)
    active = ExposureAlertQuerySet.as_manager()           # convenience alias (e.g., ExposureAlert.active.active_for(user))

    class Meta:
        indexes = [
            # Fast check for “does this user have any active alerts?”
            models.Index(fields=["user", "acknowledged_at", "expires_at"]),
            # Keep your earlier helpful indexes too (optional but nice for history/cleanup)
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_active(self) -> bool:
        return (self.acknowledged_at is None) and (self.expires_at > timezone.now())

    def __str__(self):
        return f"ExposureAlert(user={self.user_id}, active={self.is_active})"
