from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "type",
        "status",
        "preferred_date",
        "created_at"
    )
    list_filter = (
        "status",
        "type",
        "created_at",
        "preferred_date"
    )
    search_fields = (
        "user__username",
        "address",
        "notes"
    )
    readonly_fields = ("created_at",)
