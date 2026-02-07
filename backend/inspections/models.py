from django.db import models


class Inspection(models.Model):
    CLASSIFICATION_CHOICES = [
        ("OAI", "Official Action Indicated"),
        ("VAI", "Voluntary Action Indicated"),
        ("NAI", "No Action Indicated"),
    ]

    # Core FDA data
    firm_name = models.CharField(max_length=512, db_index=True)
    inspection_date = models.DateField(db_index=True)
    city = models.CharField(max_length=255, blank=True, default="")
    country = models.CharField(max_length=255, blank=True, default="", db_index=True)
    classification = models.CharField(
        max_length=3,
        choices=CLASSIFICATION_CHOICES,
        db_index=True,
    )
    fda_event_id = models.CharField(max_length=64, unique=True, db_index=True)
    raw_data = models.JSONField()

    # Auditability — every record is fully traceable
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    change_log = models.JSONField(default=list)
    # change_log entry format:
    #   {"ts": "2024-01-15T10:30:00Z", "event": "initial_ingest"}
    #   {"ts": "...", "field": "classification", "old": "VAI", "new": "OAI"}

    # AWS S3 — pointer back to the immutable raw source in the data lake
    s3_archive_key = models.CharField(max_length=512, blank=True, default="")
    # e.g. "raw/2024/01/15/event_12345.json"

    # ML risk prediction (0.0 = lowest risk, 1.0 = highest)
    predicted_risk_score = models.FloatField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-inspection_date"]
        indexes = [
            models.Index(fields=["country", "classification"]),
            models.Index(fields=["inspection_date", "classification"]),
            models.Index(fields=["predicted_risk_score"]),
        ]

    def __str__(self):
        return f"{self.firm_name} — {self.classification} ({self.inspection_date})"
