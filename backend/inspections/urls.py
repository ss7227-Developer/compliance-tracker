from django.urls import path
from .views import InspectionDetailView, InspectionListView, stats_view, trigger_fetch

urlpatterns = [
    path("inspections/", InspectionListView.as_view(), name="inspection-list"),
    path("inspections/<int:pk>/", InspectionDetailView.as_view(), name="inspection-detail"),
    path("stats/", stats_view, name="stats"),
    path("fetch/", trigger_fetch, name="trigger-fetch"),
]
