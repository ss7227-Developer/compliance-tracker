"""
Management command: score_risk

Runs the Scikit-learn risk heuristic against all firms in the database
and updates the predicted_risk_score field on every Inspection row.

Run this after each data ingestion to keep risk scores current.

Usage:
    python manage.py score_risk
    python manage.py score_risk --top 20     # print top 20 highest-risk firms
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Compute and persist predicted_risk_score for all firms"

    def add_arguments(self, parser):
        parser.add_argument(
            "--top",
            type=int,
            default=10,
            help="Number of highest-risk firms to display (default: 10)",
        )

    def handle(self, *args, **options):
        from inspections.risk import compute_risk_scores

        self.stdout.write("Computing risk scores...")
        results = compute_risk_scores()

        if not results:
            self.stdout.write(
                self.style.WARNING(
                    "No inspections found in the database. "
                    "Run fetch_fda_data first."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Scored {len(results)} firms successfully.\n")
        )

        top_n = options["top"]
        self.stdout.write(f"Top {top_n} highest-risk firms:")
        self.stdout.write("-" * 60)
        for i, (firm, score) in enumerate(results[:top_n], 1):
            risk_label = (
                "HIGH  " if score >= 0.7
                else "MEDIUM" if score >= 0.4
                else "LOW   "
            )
            self.stdout.write(f"  {i:2}. [{risk_label}] {score:.4f}  {firm}")
