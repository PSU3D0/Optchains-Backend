from django.core.management.base import BaseCommand

from ..._setup import buildSPY

class Command(BaseCommand):
    help = "Loads initial stock and chain data into database"

    def handle(self, *args, **kwargs):
        buildSPY()
        print("Successfully built database")