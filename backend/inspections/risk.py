"""
Scikit-learn risk prediction heuristic for FDA inspection facilities.

Algorithm: Weighted linear combination of 3 features per firm.
  - OAI rate              (weight 0.50) — % of inspections classified OAI
  - Inspection frequency  (weight 0.30) — total inspections, MinMax normalized
  - Recent OAI flag       (weight 0.20) — 1.0 if any OAI in last 365 days, else 0.0

Output: predicted_risk_score in [0.0, 1.0] stored on every Inspection row for that firm.

Why this approach:
  - Frequency matters because firms with more interactions have more opportunities
    for serious findings; normalizing prevents large-firm bias.
  - Recency captures whether the firm is in an active enforcement cycle right now.
  - OAI rate is the strongest signal: consistent OAI history is the best predictor
    of future OAI findings.
  - MinMaxScaler ensures all features sit in [0, 1] before weighting.
"""

import logging
from datetime import date, timedelta

import numpy as np
from django.db.models import Count, Q
from sklearn.preprocessing import MinMaxScaler

from .models import Inspection

logger = logging.getLogger(__name__)

WEIGHTS = np.array([0.5, 0.3, 0.2])  # [oai_rate, frequency, recent_oai]
RECENCY_WINDOW_DAYS = 365


def compute_risk_scores() -> list[tuple[str, float]]:
    """
    Compute and persist predicted_risk_score for every firm in the database.

    Returns:
        List of (firm_name, score) tuples sorted by score descending.
        Empty list if the database has no records.
    """
    one_year_ago = date.today() - timedelta(days=RECENCY_WINDOW_DAYS)

    firms = list(
        Inspection.objects.values("firm_name").annotate(
            total=Count("id"),
            oai_count=Count("id", filter=Q(classification="OAI")),
            recent_oai=Count(
                "id",
                filter=Q(classification="OAI", inspection_date__gte=one_year_ago),
            ),
        )
    )

    if not firms:
        logger.warning("compute_risk_scores: no inspections found in database")
        return []

    # Build feature matrix [n_firms, 3]
    X = np.array(
        [
            [
                f["oai_count"] / f["total"] if f["total"] > 0 else 0.0,
                float(f["total"]),
                1.0 if f["recent_oai"] > 0 else 0.0,
            ]
            for f in firms
        ],
        dtype=float,
    )

    # Normalize frequency column (index 1) to [0, 1]
    if X[:, 1].max() > 0:
        X[:, 1] = MinMaxScaler().fit_transform(X[:, 1].reshape(-1, 1)).flatten()

    # Weighted dot product → scores in [0, 1]
    scores = X @ WEIGHTS

    results: list[tuple[str, float]] = []
    for i, firm in enumerate(firms):
        score = round(float(scores[i]), 4)
        Inspection.objects.filter(firm_name=firm["firm_name"]).update(
            predicted_risk_score=score
        )
        results.append((firm["firm_name"], score))

    results.sort(key=lambda x: x[1], reverse=True)
    logger.info(f"compute_risk_scores: scored {len(results)} firms")
    return results
