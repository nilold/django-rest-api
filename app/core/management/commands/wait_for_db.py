import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """"Django to pause execution until database is available"""
    DB_WAIT_PERIOD = 1

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')

        db_conn = None

        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write(f"Database unavailable. Waiting {self.DB_WAIT_PERIOD} seconds.")
                time.sleep(self.DB_WAIT_PERIOD)

        self.stdout.write(self.style.SUCCESS('Database available'))
