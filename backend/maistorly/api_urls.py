from django.urls import include, path

urlpatterns = [
    path("", include("jobs.api_urls")),
    path("", include("craftsmen.api_urls")),
]
