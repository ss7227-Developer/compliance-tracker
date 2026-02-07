"""
Management command: wait_for_db

Polls the default database connection until it becomes available.
Used in docker-compose to block the API and Celery services until
PostgreSQL (or RDS) is ready to accept connections.

Usage:
    python manage.py wait_for_db
"""

import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Waits for the database to be available before proceeding"

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        max_attempts = 30

        for attempt in range(1, max_attempts + 1):
            try:
                conn = connections["default"]
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS("Database is available!"))
                return
            except OperationalError:
                self.stdout.write(
                    f"  Database unavailable (attempt {attempt}/{max_attempts}), "
                    f"retrying in 1 second..."
                )
                time.sleep(1)

        raise SystemExit(
            f"Could not connect to the database after {max_attempts} attempts. "
            "Check your DATABASE_URL and that the database service is running."
        )
