import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """"Django to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")

        db_conn = None

        while not db_conn:
            try:
                db_conn = connections["default"]
            except OperationalError:
                time.sleep(1)
                self.stdout.write("Database unavailable. Waiting 1 second.")

        self.stdout.write(self.style.SUCCESS("Database available"))
