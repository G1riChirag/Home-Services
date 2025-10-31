from django.urls import path
from .views import StartPaymentView, InvoiceDetailView, WebhookView

app_name = "payments"

urlpatterns = [
    path("bookings/<int:booking_id>/pay/", StartPaymentView.as_view(), name="start"),
    path("invoices/<str:invoice_number>/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("webhooks/provider/", WebhookView.as_view(), name="webhook"),
]
