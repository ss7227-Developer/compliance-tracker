import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Inspection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("firm_name", models.CharField(db_index=True, max_length=512)),
                ("inspection_date", models.DateField(db_index=True)),
                ("city", models.CharField(blank=True, default="", max_length=255)),
                (
                    "country",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=255
                    ),
                ),
                (
                    "classification",
                    models.CharField(
                        choices=[
                            ("OAI", "Official Action Indicated"),
                            ("VAI", "Voluntary Action Indicated"),
                            ("NAI", "No Action Indicated"),
                        ],
                        db_index=True,
                        max_length=3,
                    ),
                ),
                (
                    "fda_event_id",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("raw_data", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("change_log", models.JSONField(default=list)),
                (
                    "s3_archive_key",
                    models.CharField(blank=True, default="", max_length=512),
                ),
                (
                    "predicted_risk_score",
                    models.FloatField(blank=True, db_index=True, null=True),
                ),
            ],
            options={
                "ordering": ["-inspection_date"],
            },
        ),
        migrations.AddIndex(
            model_name="inspection",
            index=models.Index(
                fields=["country", "classification"],
                name="inspections_country_classif_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="inspection",
            index=models.Index(
                fields=["inspection_date", "classification"],
                name="inspections_date_classif_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="inspection",
            index=models.Index(
                fields=["predicted_risk_score"],
                name="inspections_risk_score_idx",
            ),
        ),
    ]
