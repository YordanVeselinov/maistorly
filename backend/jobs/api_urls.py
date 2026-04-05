from django.urls import path

from .api_views import JobRequestDetailAPIView, JobRequestListCreateAPIView

urlpatterns = [
    path("jobs/", JobRequestListCreateAPIView.as_view(), name="api-job-list"),
    path("jobs/<int:pk>/", JobRequestDetailAPIView.as_view(), name="api-job-detail"),
]
