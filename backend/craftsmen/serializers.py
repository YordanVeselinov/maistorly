from rest_framework import serializers

from .models import CraftsmanProfile


class CraftsmanProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    skills = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = CraftsmanProfile
        fields = (
            "id",
            "username",
            "email",
            "display_name",
            "bio",
            "phone",
            "city",
            "country",
            "is_available",
            "skills",
            "created_at",
            "updated_at",
        )
