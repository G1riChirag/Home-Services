from datetime import timedelta
import io
import qrcode

from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from utils.mixins import BreadcrumbsMixin
from .models import Booking, ContactEvent, ExposureAlert, Review  # ExposureAlert imported for future use
from .forms import BookingForm, ReviewForm

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


class BookingCreateView(LoginRequiredMixin, BreadcrumbsMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"
    success_url = reverse_lazy("booking-list")

    # bookings/views.py — inside BookingCreateView.form_valid
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = "Pending"

        # Fallback (in case the form didn’t set it for any reason)
        if not form.instance.quoted_price_cents:
            if form.instance.package and form.instance.package.price_cents:
                form.instance.quoted_price_cents = form.instance.package.price_cents
            elif form.instance.service and form.instance.service.base_price_cents:
                form.instance.quoted_price_cents = form.instance.service.base_price_cents

        return super().form_valid(form)



    def get_breadcrumbs(self):
        return [
            {"label": "Home", "url": reverse("home")},
            {"label": "Bookings"},
        ]


class BookingListView(LoginRequiredMixin, BreadcrumbsMixin, ListView):
    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by("-created_at")

    def get_breadcrumbs(self):
        return [
            {"label": "Home", "url": reverse("home")},
            {"label": "Bookings"},
        ]


class BookingDetailView(LoginRequiredMixin, BreadcrumbsMixin, DetailView):
    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["breadcrumbs"] = [
            {"label": "Home", "url": reverse("home")},
            {"label": "Bookings", "url": reverse("booking-list")},
            {"label": "Booking Details"},
        ]
        return ctx


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"
    success_url = reverse_lazy("booking-list")


class BookingConfirmView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)
        if booking.status != "Pending":
            messages.error(request, "Only pending bookings can be confirmed.")
            return redirect("booking-detail", pk=booking.pk)
        booking.status = "Confirmed"
        booking.save(update_fields=["status"])
        messages.success(request, "Booking confirmed.")
        return redirect("booking-detail", pk=booking.pk)


def booking_qr(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    payload = {"bookingId": booking.id, "userId": booking.user.id, "status": booking.status}
    img = qrcode.make(str(payload))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")


@login_required
@require_http_methods(["GET", "POST"])
def booking_checkin(request, pk):
    """
    GET  -> show minimal confirm screen (works for non-owners)
    POST -> record contact between request.user and booking.owner
    """
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == "GET":
        # Minimal page; does not leak booking details
        return render(request, "bookings/checkin.html", {"booking_id": booking.pk})

    # POST: record contact
    other = booking.user
    if other == request.user:
        messages.info(request, "Self check-in ignored.")
        return redirect("booking-detail", pk=pk)

    ContactEvent.objects.create(
        user_a=request.user,
        user_b=other,
        occurred_at=timezone.now(),
        booking=booking,
    )
    messages.success(request, "Check-in recorded.")
    # Send both parties back to somewhere sensible
    return redirect("booking-detail", pk=pk) if request.user == booking.user else redirect("booking-list")

@login_required
def submit_review(request, pk):
    booking = get_object_or_404(Booking, id=pk, user=request.user)

    if booking.status != "Done":
        messages.error(request, "You can only review completed bookings.")
        return redirect("booking-detail", pk=booking.id)

    if hasattr(booking, "review"):
        messages.info(request, "You have already submitted a review for this booking.")
        return redirect("booking-detail", pk=booking.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            messages.success(request, "Thank you for your feedback.")
            return redirect("booking-detail", pk=booking.id)
    else:
        form = ReviewForm()

    return render(request, "bookings/review_form.html", {"form": form, "booking": booking})