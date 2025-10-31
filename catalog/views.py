
from django.views.generic import ListView, DetailView
from django.urls import reverse
from .models import Service, ServicePackage
from utils.mixins import BreadcrumbsMixin
from bookings.models import Review


class ServiceListView(BreadcrumbsMixin, ListView):
    template_name = "catalog/services_list.html"
    model = Service
    context_object_name = "services"

    def get_queryset(self):
        qs = super().get_queryset()
        for s in qs:
            reviews = Review.objects.filter(booking__service=s)
            if reviews.exists():
                average_rating = sum(r.rating for r in reviews) / reviews.count()
                s.average_rating = round(average_rating, 1)
            else:
                s.average_rating = None
        return qs
    
    def get_breadcrumbs(self):
        return [
            {"label": "Home", "url": reverse("home")},
            {"label": "Services"},
        ]

class PackageListView(BreadcrumbsMixin, ListView):
    template_name = "catalog/packages_list.html"
    model = ServicePackage
    context_object_name = "packages"

    def get_queryset(self):
        qs = super().get_queryset()
        for p in qs:
            reviews = Review.objects.filter(booking__package=p)
            if reviews.exists():
                average_rating = sum(r.rating for r in reviews) / reviews.count()
                p.average_rating = round(average_rating, 1)
            else:
                p.average_rating = None
        return qs

    def get_breadcrumbs(self):
        return [
            {"label": "Home", "url": reverse("home")},
            {"label": "Packages"},
        ]

class PackageDetailView(BreadcrumbsMixin, DetailView):
    template_name = "catalog/package_detail.html"
    model = ServicePackage
    context_object_name = "package"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        b = self.object
        ctx["breadcrumbs"] = [
            {"label": "Home", "url": reverse("home")},
            {"label": "Packages", "url": reverse("packages")},
            {"label": "Packages Details"},
        ]

        reviews = Review.objects.filter(booking__package=b)
        ctx["reviews"] = reviews

        if (reviews.exists()):
            average_rating = sum(r.rating for r in reviews) / reviews.count()
            ctx["average_rating"] = round(average_rating, 1)
        else:
            ctx["average_rating"] = None
        
        return ctx
