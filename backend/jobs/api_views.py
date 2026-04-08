from rest_framework import generics, permissions

from accounts.signals import CLIENTS_GROUP

from .models import JobRequest
from .serializers import JobRequestSerializer


class IsClientUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name=CLIENTS_GROUP).exists()
        )


class JobRequestListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = JobRequestSerializer

    def get_queryset(self):
        queryset = JobRequest.objects.select_related("owner").prefetch_related(
            "categories",
            "required_skills",
            "images",
            "offers__craftsman",
        )

        city = self.request.query_params.get("city", "").strip()
        category = self.request.query_params.get("category", "").strip()
        status = self.request.query_params.get("status", "").strip()

        if city:
            queryset = queryset.filter(city__iexact=city)

        if category:
            queryset = queryset.filter(categories__id=category)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.distinct()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsClientUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class JobRequestDetailAPIView(generics.RetrieveAPIView):
    queryset = JobRequest.objects.select_related("owner").prefetch_related(
        "categories",
        "required_skills",
        "images",
        "offers__craftsman",
    )
    serializer_class = JobRequestSerializer
    permission_classes = [permissions.AllowAny]
