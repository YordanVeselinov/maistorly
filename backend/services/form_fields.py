from django import forms

from .models import Category, Skill


def category_queryset():
    return Category.objects.order_by("name")


def skill_queryset():
    return Skill.objects.select_related("category").order_by("category__name", "name")


class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class CategoryMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class SkillMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if obj.category_id:
            return f"{obj.category.name} - {obj.name}"
        return obj.name
