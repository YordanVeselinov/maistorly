from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CraftsmanProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("display_name", models.CharField(blank=True, max_length=120)),
                ("bio", models.TextField(blank=True)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("country", models.CharField(blank=True, max_length=100)),
                ("is_available", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("skills", models.ManyToManyField(blank=True, related_name="craftsmen", to="services.skill")),
                ("user", models.OneToOneField(on_delete=models.deletion.CASCADE, related_name="craftsman_profile", to="accounts.user")),
            ],
            options={
                "ordering": ("user__username",),
            },
        ),
    ]
