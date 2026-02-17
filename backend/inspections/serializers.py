from rest_framework import serializers
from .models import Inspection


class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = [
            "id",
            "firm_name",
            "inspection_date",
            "city",
            "country",
            "classification",
            "fda_event_id",
            "predicted_risk_score",
            "s3_archive_key",
            "created_at",
            "updated_at",
        ]
        # raw_data excluded from list view to keep payload lean


class InspectionDetailSerializer(InspectionSerializer):
    """Full serializer including raw_data and change_log for detail endpoints."""

    class Meta(InspectionSerializer.Meta):
        fields = InspectionSerializer.Meta.fields + ["raw_data", "change_log"]
