from django import forms
from django.utils.text import slugify

from .form_fields import CategoryChoiceField, category_queryset
from .models import Category, Skill


class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "description")
        labels = {
            "name": "Category name",
            "description": "Description",
        }
        help_texts = {
            "name": "Add a service category that is missing from the list.",
            "description": "Optional. Briefly describe when this category should be used.",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Window repair",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional notes about this category.",
                    "rows": 4,
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Please enter a category name.")

        slug = slugify(name)
        if Category.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("This category already exists.")
        if Category.objects.filter(slug=slug).exists():
            raise forms.ValidationError("A category with a similar name already exists.")

        return name

    def clean_description(self):
        return self.cleaned_data.get("description", "").strip()


class SkillCreateForm(forms.ModelForm):
    category = CategoryChoiceField(
        label="Category",
        queryset=category_queryset(),
        empty_label="Select a category",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = Skill
        fields = ("category", "name", "description")
        labels = {
            "name": "Skill name",
            "description": "Description",
        }
        help_texts = {
            "category": "Choose the category this skill belongs to.",
            "name": "Add a specific skill that is missing from the list.",
            "description": "Optional. Briefly describe this skill.",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Window sealing",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional notes about this skill.",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = category_queryset()

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Please enter a skill name.")
        return name

    def clean_description(self):
        return self.cleaned_data.get("description", "").strip()

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        name = cleaned_data.get("name")

        if category and name:
            if Skill.objects.filter(category=category, name__iexact=name).exists():
                self.add_error("name", "This skill already exists in the selected category.")
            slug = slugify(f"{category.slug or category.name}-{name}")
            if Skill.objects.filter(slug=slug).exists():
                self.add_error("name", "A skill with a similar name already exists.")

        return cleaned_data

    def save(self, commit=True):
        skill = super().save(commit=False)
        if not skill.slug and skill.category_id:
            skill.slug = slugify(f"{skill.category.slug or skill.category.name}-{skill.name}")
        if commit:
            skill.save()
            self.save_m2m()
        return skill
