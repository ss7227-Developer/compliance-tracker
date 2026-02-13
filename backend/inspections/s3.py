"""
AWS S3 helper for archiving raw OpenFDA records.

S3 key structure: raw/{YYYY}/{MM}/{DD}/{fda_event_id}.json

This provides an immutable, versioned data lake of source records so that
auditors can always trace a normalized Inspection row back to the exact
API response that created it. Errors are logged but never raised — an S3
outage should never block the data ingestion pipeline.
"""

import json
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_s3_client():
    """Return a boto3 S3 client using credentials from Django settings."""
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    )


def upload_batch_to_s3(records: list, batch_date: str) -> dict[str, str]:
    """
    Uploads individual OpenFDA records to S3.

    Args:
        records:    List of raw OpenFDA JSON dicts from the API response.
        batch_date: ISO date string "YYYY-MM-DD" used to partition the S3 path.

    Returns:
        Dict mapping fda_event_id → s3_key for successfully uploaded records.
        Empty dict if AWS credentials are not configured.
    """
    if not settings.AWS_ACCESS_KEY_ID:
        logger.warning("AWS_ACCESS_KEY_ID not set — skipping S3 archive upload")
        return {}

    try:
        s3 = _get_s3_client()
    except Exception as exc:
        logger.error(f"Failed to initialise S3 client: {exc}")
        return {}

    bucket = settings.S3_RAW_BUCKET
    year, month, day = batch_date.split("-")
    uploaded: dict[str, str] = {}

    for record in records:
        event_id = str(record.get("event_id", "unknown"))
        key = f"raw/{year}/{month}/{day}/{event_id}.json"
        try:
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(record, default=str),
                ContentType="application/json",
                Metadata={
                    "source": "openfda-drug-enforcement",
                    "event_id": event_id,
                    "ingest_date": batch_date,
                },
            )
            uploaded[event_id] = key
        except (BotoCoreError, ClientError) as exc:
            logger.error(f"S3 upload failed for event_id={event_id}: {exc}")

    logger.info(
        f"S3 archive: uploaded {len(uploaded)}/{len(records)} records to "
        f"s3://{bucket}/raw/{year}/{month}/{day}/"
    )
    return uploaded
