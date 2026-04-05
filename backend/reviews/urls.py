from django.urls import path

from .views import ReviewCreateView, ReviewDeleteView, ReviewListByCraftsmanView, ReviewUpdateView

app_name = "reviews"

urlpatterns = [
    path("craftsmen/<int:pk>/", ReviewListByCraftsmanView.as_view(), name="craftsman_reviews"),
    path("jobs/<int:job_pk>/craftsmen/<int:craftsman_pk>/create/", ReviewCreateView.as_view(), name="review_create"),
    path("<int:pk>/edit/", ReviewUpdateView.as_view(), name="review_update"),
    path("<int:pk>/delete/", ReviewDeleteView.as_view(), name="review_delete"),
]
