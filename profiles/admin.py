from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "vaccination_status",
        "vaccination_uploaded_at",
        "vaccination_verified",
        "covid_vaccinated",
        "language",
        "citizenship",
        "consent_updated_at",
    )
    list_filter = (
        "vaccination_verified",
        "covid_vaccinated",
        "consent_marketing",
        "consent_healthdata",
    )
    search_fields = (
        "user__username",
        "name",
        "language",
        "citizenship",
    )
    readonly_fields = ("consent_updated_at", "consent_version")
    exclude = ("totp_secret",)
