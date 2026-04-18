from django.db import migrations


SEED_DATA = {
    "Plumbing": [
        "Pipe Repair",
        "Leak Detection",
        "Faucet Installation",
        "Drain Cleaning",
    ],
    "Electrical": [
        "Wiring",
        "Light Installation",
        "Outlet Repair",
        "Fuse Box Inspection",
    ],
    "Painting": [
        "Interior Painting",
        "Exterior Painting",
        "Wall Preparation",
        "Color Consultation",
    ],
    "Carpentry": [
        "Door Repair",
        "Furniture Assembly",
        "Cabinet Installation",
        "Wood Flooring",
    ],
    "Masonry": [
        "Tile Installation",
        "Wall Repair",
        "Plastering",
        "Concrete Repair",
    ],
    "HVAC": [
        "Air Conditioner Service",
        "Heating Repair",
        "Ventilation Maintenance",
    ],
    "Appliance Repair": [
        "Washing Machine Repair",
        "Oven Repair",
        "Refrigerator Repair",
    ],
    "Cleaning": [
        "Deep Cleaning",
        "Move Out Cleaning",
        "Upholstery Cleaning",
    ],
    "Roofing": [
        "Roof Leak Repair",
        "Gutter Cleaning",
        "Roof Inspection",
    ],
    "Landscaping": [
        "Garden Maintenance",
        "Lawn Mowing",
        "Fence Repair",
    ],
}


def slugify_value(value):
    return value.lower().replace(" ", "-")


def seed_categories_and_skills(apps, schema_editor):
    Category = apps.get_model("services", "Category")
    Skill = apps.get_model("services", "Skill")

    for category_name, skill_names in SEED_DATA.items():
        category_slug = slugify_value(category_name)
        category = (
            Category.objects.filter(slug=category_slug).first()
            or Category.objects.filter(name=category_name).first()
        )
        if category is None:
            category = Category.objects.create(
                name=category_name,
                slug=category_slug,
            )

        for skill_name in skill_names:
            skill_slug = f"{category_slug}-{slugify_value(skill_name)}"
            if Skill.objects.filter(slug=skill_slug).exists():
                continue
            if Skill.objects.filter(category=category, name=skill_name).exists():
                continue
            Skill.objects.create(
                category=category,
                name=skill_name,
                slug=skill_slug,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories_and_skills, migrations.RunPython.noop),
    ]
