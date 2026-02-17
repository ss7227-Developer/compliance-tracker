from datetime import date, timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .filters import InspectionFilter
from .models import Inspection
from .serializers import InspectionDetailSerializer, InspectionSerializer


class InspectionListView(generics.ListAPIView):
    """
    GET /api/inspections/
    Supports filtering by: country, classification, firm_name, date_from, date_to
    Supports search across: firm_name, city, country
    Supports ordering by: inspection_date, firm_name, country, classification, predicted_risk_score
    """

    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    filterset_class = InspectionFilter
    search_fields = ["firm_name", "city", "country"]
    ordering_fields = [
        "inspection_date",
        "firm_name",
        "country",
        "classification",
        "predicted_risk_score",
    ]
    ordering = ["-inspection_date"]


class InspectionDetailView(generics.RetrieveAPIView):
    """GET /api/inspections/<id>/ — full detail including raw_data and change_log"""

    queryset = Inspection.objects.all()
    serializer_class = InspectionDetailSerializer


@api_view(["GET"])
def stats_view(request):
    """
    GET /api/stats/
    Returns aggregated metrics for the dashboard:
      - total_inspections
      - oai_percentage
      - top_countries (top 5)
      - monthly_trend (last 12 months)
    All computed in 4 DB queries — no N+1.
    """
    total = Inspection.objects.count()
    oai_count = Inspection.objects.filter(classification="OAI").count()
    oai_pct = round(oai_count / total * 100, 1) if total else 0

    top_countries = list(
        Inspection.objects.values("country")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    twelve_months_ago = date.today() - timedelta(days=365)
    monthly_trend = list(
        Inspection.objects.filter(inspection_date__gte=twelve_months_ago)
        .annotate(month=TruncMonth("inspection_date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    return Response(
        {
            "total_inspections": total,
            "oai_percentage": oai_pct,
            "top_countries": top_countries,
            "monthly_trend": [
                {"month": t["month"].strftime("%Y-%m"), "count": t["count"]}
                for t in monthly_trend
            ],
        }
    )


@api_view(["POST"])
def trigger_fetch(request):
    """
    POST /api/fetch/
    Enqueues a background Celery task to fetch FDA data.
    Body: {"limit": 500}  (optional, default 500)
    Returns: {"task_id": "..."} with HTTP 202 Accepted
    """
    from .tasks import fetch_fda_batch

    limit = int(request.data.get("limit", 500))
    task = fetch_fda_batch.delay(limit=limit)
    return Response({"task_id": str(task.id)}, status=status.HTTP_202_ACCEPTED)
