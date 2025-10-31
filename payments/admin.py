from django.contrib import admin
from .models import Payment, Invoice

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "user", "provider", "amount_cents", "currency", "status", "created_at")
    list_filter = ("provider", "status", "currency", "created_at")
    search_fields = ("booking__id", "user__username", "provider_intent_id", "provider_charge_id")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "booking", "user", "total_cents", "currency", "issued_at")
    list_filter = ("currency", "issued_at")
    search_fields = ("number", "booking__id", "user__username")
    readonly_fields = ("issued_at",)
