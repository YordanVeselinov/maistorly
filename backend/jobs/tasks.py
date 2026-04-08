from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Offer


@shared_task
def send_offer_notification_email(offer_id):
    offer = (
        Offer.objects.select_related("job_request", "craftsman", "job_request__owner")
        .filter(pk=offer_id)
        .first()
    )
    if offer is None:
        return "offer-not-found"

    owner_email = offer.job_request.owner.email
    if not owner_email:
        return "owner-email-missing"

    send_mail(
        subject=f"New offer for {offer.job_request.title}",
        message=(
            f"You have received a new offer for your job request \"{offer.job_request.title}\".\n\n"
            f"Craftsman: {offer.craftsman.get_username()}\n"
            f"Proposed price: {offer.proposed_price}\n"
            f"Estimated days: {offer.estimated_days if offer.estimated_days is not None else 'Not specified'}\n\n"
            f"Message:\n{offer.message}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[owner_email],
        fail_silently=False,
    )
    return "email-sent"
