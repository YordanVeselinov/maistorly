from django.contrib import admin

from .models import CraftsmanProfile


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
