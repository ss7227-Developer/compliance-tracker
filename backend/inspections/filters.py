import django_filters
from .models import Inspection


class InspectionFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(lookup_expr="iexact")
    classification = django_filters.ChoiceFilter(
        choices=Inspection.CLASSIFICATION_CHOICES
    )
    firm_name = django_filters.CharFilter(lookup_expr="icontains")
    date_from = django_filters.DateFilter(
        field_name="inspection_date", lookup_expr="gte"
    )
    date_to = django_filters.DateFilter(
        field_name="inspection_date", lookup_expr="lte"
    )

    class Meta:
        model = Inspection
        fields = ["country", "classification", "firm_name", "date_from", "date_to"]
