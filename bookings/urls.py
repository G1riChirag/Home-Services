from django.urls import path
from .views import (
    BookingCreateView, BookingListView, BookingDetailView, BookingUpdateView,
    BookingConfirmView, booking_qr, booking_checkin, submit_review
)

urlpatterns = [
    path("bookings/new/", BookingCreateView.as_view(), name="booking-new"),
    path("bookings/", BookingListView.as_view(), name="booking-list"),
    path("bookings/<int:pk>/", BookingDetailView.as_view(), name="booking-detail"),
    path("bookings/<int:pk>/edit/", BookingUpdateView.as_view(), name="booking-edit"),
    path("bookings/<int:pk>/confirm/", BookingConfirmView.as_view(), name="booking-confirm"),
    path("bookings/<int:pk>/qr/", booking_qr, name="booking-qr"),
    path("bookings/<int:pk>/checkin/", booking_checkin, name="booking-checkin"),
    path("bookings/<int:pk>/review/", submit_review, name="booking-review"),
]
