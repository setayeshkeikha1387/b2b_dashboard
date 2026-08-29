import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("message", models.CharField(max_length=255)),
                ("link", models.CharField(blank=True, help_text="Relative URL the notification should take the user to when clicked.", max_length=255)),
                ("is_read", models.BooleanField(default=False, db_index=True)),
                ("emailed", models.BooleanField(default=False, help_text="Whether this was also sent via email.")),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Notification",
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
    ]
