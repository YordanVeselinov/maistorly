from django.urls import path

from .views import (
    JobRequestCreateView,
    JobRequestDeleteView,
    JobRequestDetailView,
    JobRequestListView,
    JobRequestUpdateView,
    MyJobRequestListView,
    MyReceivedOffersListView,
    MyOffersListView,
    OfferCreateView,
)

app_name = "jobs"

urlpatterns = [
    path("", JobRequestListView.as_view(), name="job_list"),
    path("mine/", MyJobRequestListView.as_view(), name="my_jobs"),
    path("offers/received/", MyReceivedOffersListView.as_view(), name="my_received_offers"),
    path("create/", JobRequestCreateView.as_view(), name="job_create"),
    path("offers/mine/", MyOffersListView.as_view(), name="my_offers"),
    path("<int:pk>/", JobRequestDetailView.as_view(), name="job_detail"),
    path("<int:pk>/edit/", JobRequestUpdateView.as_view(), name="job_update"),
    path("<int:pk>/delete/", JobRequestDeleteView.as_view(), name="job_delete"),
    path("<int:pk>/offers/create/", OfferCreateView.as_view(), name="offer_create"),
]
