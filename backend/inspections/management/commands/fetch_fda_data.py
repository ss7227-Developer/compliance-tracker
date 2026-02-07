"""
Management command: fetch_fda_data

Enqueues a Celery task to fetch drug enforcement records from OpenFDA,
archive them to S3, and upsert them into the database.

Usage:
    python manage.py fetch_fda_data             # fetch 500 records (default)
    python manage.py fetch_fda_data --limit 2000
    python manage.py fetch_fda_data --limit 100 --skip 500
    python manage.py fetch_fda_data --sync      # run synchronously (no Celery)
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Fetch FDA drug enforcement data and ingest into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=500,
            help="Maximum number of records to fetch (default: 500)",
        )
        parser.add_argument(
            "--skip",
            type=int,
            default=0,
            help="Number of records to skip at the start (default: 0)",
        )
        parser.add_argument(
            "--sync",
            action="store_true",
            default=False,
            help="Run synchronously in this process instead of via Celery worker",
        )

    def handle(self, *args, **options):
        from inspections.tasks import fetch_fda_batch

        limit = options["limit"]
        skip = options["skip"]
        sync = options["sync"]

        self.stdout.write(
            f"{'[SYNC] ' if sync else ''}Fetching up to {limit} FDA records "
            f"(skip={skip})..."
        )

        if sync:
            # Run directly in this process — useful for local dev without a Celery worker
            result = fetch_fda_batch(limit=limit, skip=skip)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done. Created={result['created']}, "
                    f"Skipped/Dupes={result['skipped']}, "
                    f"Total fetched={result['total_fetched']}"
                )
            )
        else:
            # Enqueue task — Celery worker picks it up asynchronously
            task = fetch_fda_batch.delay(limit=limit, skip=skip)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Task enqueued successfully.\n"
                    f"  Task ID: {task.id}\n"
                    f"  Monitor with: docker compose logs -f celery"
                )
            )
