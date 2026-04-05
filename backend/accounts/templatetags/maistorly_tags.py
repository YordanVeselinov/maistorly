from decimal import InvalidOperation

from django import template

register = template.Library()


@register.filter
def currency_bgn(value):
    if value in (None, ""):
        return "-"

    try:
        return f"{float(value):,.2f} BGN"
    except (TypeError, ValueError, InvalidOperation):
        return value


@register.filter
def budget_range(job_request):
    if not job_request:
        return "-"
    return f"{currency_bgn(job_request.budget_min)} - {currency_bgn(job_request.budget_max)}"


@register.filter
def status_badge_class(value):
    mapping = {
        "open": "bg-primary-subtle text-primary-emphasis",
        "in_progress": "bg-warning-subtle text-warning-emphasis",
        "completed": "bg-success-subtle text-success-emphasis",
        "cancelled": "bg-secondary-subtle text-secondary-emphasis",
        "pending": "bg-warning-subtle text-warning-emphasis",
        "accepted": "bg-success-subtle text-success-emphasis",
        "rejected": "bg-danger-subtle text-danger-emphasis",
        "withdrawn": "bg-secondary-subtle text-secondary-emphasis",
    }
    return mapping.get(value, "bg-light text-dark")


@register.filter
def boolean_badge_class(value):
    return "bg-success-subtle text-success-emphasis" if value else "bg-secondary-subtle text-secondary-emphasis"


@register.filter
def has_group(user, group_name):
    if not getattr(user, "is_authenticated", False):
        return False
    return user.groups.filter(name=group_name).exists()

