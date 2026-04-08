from django.contrib import admin

from .models import JobRequest, JobRequestImage, Offer


class JobRequestImageInline(admin.TabularInline):
    model = JobRequestImage
    extra = 1


@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "city",
        "budget_min",
        "budget_max",
        "preferred_date",
        "status",
        "created_at",
    )
    list_filter = ("status", "city", "categories", "required_skills", "created_at")
    search_fields = (
        "title",
        "description",
        "city",
        "owner__username",
        "owner__email",
    )
    filter_horizontal = ("categories", "required_skills")
    inlines = [JobRequestImageInline]


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job_request",
        "craftsman",
        "proposed_price",
        "estimated_days",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "job_request__title",
        "craftsman__username",
        "craftsman__email",
        "message",
    )

