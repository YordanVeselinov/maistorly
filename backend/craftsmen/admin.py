from django.contrib import admin

from .models import CraftsmanProfile, ServiceListing, ServiceListingImage


@admin.register(CraftsmanProfile)
class CraftsmanProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "display_name",
        "city",
        "country",
        "is_available",
        "created_at",
    )
    list_filter = ("is_available", "country", "city")
    search_fields = ("user__username", "user__email", "display_name", "city", "country")
    filter_horizontal = ("skills",)


class ServiceListingImageInline(admin.TabularInline):
    model = ServiceListingImage
    extra = 1


@admin.register(ServiceListing)
class ServiceListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "craftsman",
        "rough_price",
        "category",
        "created_at",
    )
    list_filter = ("category", "created_at")
    search_fields = ("title", "craftsman__username", "craftsman__email", "description")
    filter_horizontal = ("skills",)
    inlines = [ServiceListingImageInline]
