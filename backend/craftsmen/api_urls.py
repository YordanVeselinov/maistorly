from django.urls import path

from .api_views import CraftsmanDetailAPIView, CraftsmanListAPIView

urlpatterns = [
    path("craftsmen/", CraftsmanListAPIView.as_view(), name="api-craftsman-list"),
    path("craftsmen/<int:pk>/", CraftsmanDetailAPIView.as_view(), name="api-craftsman-detail"),
]
