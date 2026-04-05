from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from services.models import Category, Skill

from .models import JobRequest, Offer


class OfferSummarySerializer(serializers.ModelSerializer):
    craftsman = serializers.CharField(source="craftsman.get_username", read_only=True)

    class Meta:
        model = Offer
        fields = (
            "id",
            "craftsman",
            "proposed_price",
            "estimated_days",
            "status",
            "created_at",
        )


class JobRequestSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.get_username", read_only=True)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
    )
    required_skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        required=False,
    )
    offers = OfferSummarySerializer(many=True, read_only=True)

    class Meta:
        model = JobRequest
        fields = (
            "id",
            "owner",
            "title",
            "description",
            "city",
            "budget_min",
            "budget_max",
            "preferred_date",
            "status",
            "categories",
            "required_skills",
            "offers",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "owner",
            "offers",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        budget_min = attrs.get("budget_min", getattr(self.instance, "budget_min", None))
        budget_max = attrs.get("budget_max", getattr(self.instance, "budget_max", None))
        preferred_date = attrs.get("preferred_date", getattr(self.instance, "preferred_date", None))

        if budget_min is not None and budget_min < 0:
            raise serializers.ValidationError({"budget_min": "Minimum budget cannot be negative."})

        if budget_min is not None and budget_max is not None and budget_max < budget_min:
            raise serializers.ValidationError({"budget_max": "Maximum budget cannot be less than minimum budget."})

        if preferred_date is not None:
            from django.utils import timezone

            if preferred_date < timezone.localdate():
                raise serializers.ValidationError({"preferred_date": "Preferred date cannot be in the past."})

        return attrs

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        required_skills = validated_data.pop("required_skills", [])
        job_request = JobRequest(**validated_data)
        self._full_clean(job_request)
        job_request.save()
        if categories:
            job_request.categories.set(categories)
        if required_skills:
            job_request.required_skills.set(required_skills)
        return job_request

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        required_skills = validated_data.pop("required_skills", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        self._full_clean(instance)
        instance.save()
        if categories is not None:
            instance.categories.set(categories)
        if required_skills is not None:
            instance.required_skills.set(required_skills)
        return instance

    def _full_clean(self, instance):
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict or {"detail": exc.messages})
