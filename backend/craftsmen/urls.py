from django.urls import path

from .views import CraftsmanDetailView, CraftsmanListView, CraftsmanProfileEditView

app_name = "craftsmen"

urlpatterns = [
    path("", CraftsmanListView.as_view(), name="craftsman_list"),
    path("<int:pk>/", CraftsmanDetailView.as_view(), name="craftsman_detail"),
    path("profile/edit/<int:pk>/", CraftsmanProfileEditView.as_view(), name="profile_edit"),
]
