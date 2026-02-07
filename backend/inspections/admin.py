from django.contrib import admin
from .models import Inspection


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = [
        "firm_name",
        "inspection_date",
        "city",
        "country",
        "classification",
        "predicted_risk_score",
        "fda_event_id",
        "created_at",
    ]
    list_filter = ["classification", "country"]
    search_fields = ["firm_name", "city", "country", "fda_event_id"]
    ordering = ["-inspection_date"]
    readonly_fields = ["fda_event_id", "raw_data", "change_log", "s3_archive_key", "created_at", "updated_at"]
    date_hierarchy = "inspection_date"
