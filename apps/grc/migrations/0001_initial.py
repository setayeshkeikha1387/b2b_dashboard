import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Risk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("severity", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")], default="medium", max_length=16)),
                ("likelihood", models.CharField(choices=[("rare", "Rare"), ("unlikely", "Unlikely"), ("possible", "Possible"), ("likely", "Likely"), ("almost_certain", "Almost certain")], default="possible", max_length=16)),
                ("status", models.CharField(choices=[("open", "Open"), ("mitigating", "Mitigating"), ("closed", "Closed")], db_index=True, default="open", max_length=16)),
                ("business_unit", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="risks", to="core.businessunit")),
                ("function", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="risks", to="core.function")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="owned_risks", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Risk",
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Control",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("control_type", models.CharField(choices=[("preventive", "Preventive"), ("detective", "Detective"), ("corrective", "Corrective")], default="preventive", max_length=16)),
                ("effectiveness", models.CharField(choices=[("effective", "Effective"), ("partially_effective", "Partially effective"), ("ineffective", "Ineffective"), ("not_tested", "Not tested")], default="not_tested", max_length=24)),
                ("last_tested_at", models.DateField(blank=True, null=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="owned_controls", to=settings.AUTH_USER_MODEL)),
                ("risk", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="controls", to="grc.risk")),
            ],
            options={
                "verbose_name": "Control",
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.AddIndex(
            model_name="risk",
            index=models.Index(fields=["status", "severity"], name="grc_risk_status_7a1f2c_idx"),
        ),
    ]
