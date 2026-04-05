from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job_request",
        "reviewer",
        "craftsman",
        "rating",
        "created_at",
    )
    list_filter = ("rating", "created_at")
    search_fields = (
        "job_request__title",
        "reviewer__username",
        "reviewer__email",
        "craftsman__username",
        "craftsman__email",
        "comment",
    )

