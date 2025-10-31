from django.contrib import admin
from .models import Service, ServicePackage

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "category", 
        "base_price_cents"
    )
    search_fields = (
        "name", 
        "category"
    )
    list_filter = ("category",)

@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = (
        "title", 
        "price_cents", 
        "is_customisable"
    )
    search_fields = ("title",)
    list_filter = ("is_customisable",)
