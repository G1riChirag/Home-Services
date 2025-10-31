def exposure_banner(request):
    """
    Adds `exposure_warning` to the template context.
    True when the user has any active (unacknowledged, unexpired) exposure alerts.
    """
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}

    # Import inside the function to avoid potential import-time circulars
    try:
        from bookings.models import ExposureAlert
        has_active = ExposureAlert.active.active_for(request.user).exists()
        return {"exposure_warning": has_active}
    except Exception:
        # Be conservative—never break rendering if the DB isn't ready (e.g., during migrate)
        return {}