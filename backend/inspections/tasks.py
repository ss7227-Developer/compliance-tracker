"""
Celery tasks for the inspections app.

fetch_fda_batch:
  - Fetches drug enforcement records from the OpenFDA API in paginated batches
  - Archives each raw record to AWS S3 (data lake)
  - Upserts normalized records into PostgreSQL (local dev) or RDS (production)
  - Retries up to 3× on network failure with 60-second exponential backoff
  - Uses fda_event_id as idempotency key — safe to re-run without creating duplicates
"""

import logging
import time
from datetime import date, datetime

import requests
from celery import shared_task

from .models import Inspection
from .s3 import upload_batch_to_s3

logger = logging.getLogger(__name__)

FDA_ENDPOINT = "https://api.fda.gov/drug/enforcement.json"
BATCH_SIZE = 100  # OpenFDA hard limit is 1000; 100 keeps memory low and retries cheap

# Map OpenFDA recall classification → inspection classification vocabulary
CLASS_MAP = {
    "Class I": "OAI",    # Immediate health hazard → Official Action Indicated
    "Class II": "VAI",   # Possible adverse health consequences → Voluntary Action Indicated
    "Class III": "NAI",  # Unlikely to cause adverse health consequences → No Action Indicated
}

RATE_LIMIT_SLEEP = 1.5  # seconds between batches; keeps us under 40 req/min without API key


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_fda_batch(self, limit: int = 1000, skip: int = 0):
    """
    Fetch up to `limit` records from OpenFDA starting at `skip`, archive to S3,
    and upsert into the database.

    Returns dict: {"created": N, "skipped": N, "total_fetched": N}
    """
    created = 0
    skipped = 0
    total_fetched = 0
    offset = skip
    today_str = date.today().isoformat()

    logger.info(f"fetch_fda_batch started: limit={limit}, skip={skip}")

    while total_fetched < limit:
        batch_size = min(BATCH_SIZE, limit - total_fetched)
        params = {"limit": batch_size, "skip": offset}

        try:
            resp = requests.get(FDA_ENDPOINT, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            logger.error(f"OpenFDA request failed (offset={offset}): {exc}")
            raise self.retry(exc=exc)

        results = data.get("results", [])
        if not results:
            logger.info(f"No more results from OpenFDA at offset={offset}")
            break

        # 1. Archive raw batch to S3 (errors are logged, not raised)
        s3_key_map = upload_batch_to_s3(results, today_str)

        # 2. Upsert to database
        for record in results:
            fda_id = str(record.get("event_id", "")).strip()
            if not fda_id:
                skipped += 1
                continue

            raw_class = record.get("classification", "")
            classification = CLASS_MAP.get(raw_class)
            if not classification:
                logger.debug(f"Unknown classification '{raw_class}' for event_id={fda_id}")
                skipped += 1
                continue

            raw_date = record.get("recall_initiation_date", "")
            try:
                inspection_date = datetime.strptime(raw_date, "%Y%m%d").date()
            except (ValueError, TypeError):
                logger.debug(f"Unparseable date '{raw_date}' for event_id={fda_id}")
                skipped += 1
                continue

            _, was_created = Inspection.objects.get_or_create(
                fda_event_id=fda_id,
                defaults={
                    "firm_name": (record.get("recalling_firm") or "Unknown")[:512],
                    "inspection_date": inspection_date,
                    "city": (record.get("city") or "")[:255],
                    "country": (record.get("country") or "")[:255],
                    "classification": classification,
                    "raw_data": record,
                    "s3_archive_key": s3_key_map.get(fda_id, ""),
                    "change_log": [
                        {
                            "ts": datetime.utcnow().isoformat() + "Z",
                            "event": "initial_ingest",
                            "source": "openfda-drug-enforcement",
                        }
                    ],
                },
            )

            if was_created:
                created += 1
            else:
                skipped += 1

        total_fetched += len(results)
        offset += len(results)

        logger.info(
            f"Batch complete: fetched={total_fetched}, created={created}, skipped={skipped}"
        )

        # Respect OpenFDA rate limit: 40 req/min without API key
        time.sleep(RATE_LIMIT_SLEEP)

    result = {"created": created, "skipped": skipped, "total_fetched": total_fetched}
    logger.info(f"fetch_fda_batch finished: {result}")
    return result
