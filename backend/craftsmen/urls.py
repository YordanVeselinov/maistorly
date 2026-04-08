from django.urls import path

from .views import (
    CraftsmanDetailView,
    CraftsmanListView,
    CraftsmanProfileEditView,
    MyServiceListingListView,
    ServiceListingCreateView,
    ServiceListingDeleteView,
    ServiceListingDetailView,
    ServiceListingListView,
    ServiceListingUpdateView,
)

app_name = "craftsmen"

urlpatterns = [
    path("", CraftsmanListView.as_view(), name="craftsman_list"),
    path("services/", ServiceListingListView.as_view(), name="service_listing_list"),
    path("services/mine/", MyServiceListingListView.as_view(), name="my_service_listings"),
    path("services/create/", ServiceListingCreateView.as_view(), name="service_listing_create"),
    path("services/<int:pk>/", ServiceListingDetailView.as_view(), name="service_listing_detail"),
    path("services/<int:pk>/edit/", ServiceListingUpdateView.as_view(), name="service_listing_update"),
    path("services/<int:pk>/delete/", ServiceListingDeleteView.as_view(), name="service_listing_delete"),
    path("<int:pk>/", CraftsmanDetailView.as_view(), name="craftsman_detail"),
    path("profile/edit/<int:pk>/", CraftsmanProfileEditView.as_view(), name="profile_edit"),
]
