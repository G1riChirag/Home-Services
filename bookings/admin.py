from django.contrib import admin
from .models import Booking, Review

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

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "booking",
        "get_service",
        "rating",
        "created_at",
    )
    search_fields = (
        "booking__service__name",
    )
    readonly_fields = (
        "booking",
        "get_service",
        "rating",
        "created_at",
    )

    def get_service(self, obj):
        return obj.booking.service if obj.booking and obj.booking.service else "-"
    
    get_service.short_description = "Service"