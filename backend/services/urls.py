from django.urls import path

from .views import CategoryCreateView, SkillCreateView

app_name = "services"

urlpatterns = [
    path("categories/create/", CategoryCreateView.as_view(), name="category_create"),
    path("skills/create/", SkillCreateView.as_view(), name="skill_create"),
]
