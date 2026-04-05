from rest_framework import generics, permissions

from accounts.signals import CRAFTSMEN_GROUP

from .models import CraftsmanProfile
from .serializers import CraftsmanProfileSerializer


class CraftsmanListAPIView(generics.ListAPIView):
    serializer_class = CraftsmanProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            CraftsmanProfile.objects.select_related("user")
            .prefetch_related("skills")
            .filter(user__groups__name=CRAFTSMEN_GROUP)
            .distinct()
        )


class CraftsmanDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CraftsmanProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            CraftsmanProfile.objects.select_related("user")
            .prefetch_related("skills")
            .filter(user__groups__name=CRAFTSMEN_GROUP)
            .distinct()
        )
