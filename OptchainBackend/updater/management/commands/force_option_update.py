from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

from ...tasks import UpdateCoordinator, start_market_update

class Command(BaseCommand):
    help = "Forces options update"

    def handle(self, *args, **kwargs):
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
        except OperationalError:
            print("Could not connect to DB!")
            return

        start_market_update(UpdateCoordinator(2000))