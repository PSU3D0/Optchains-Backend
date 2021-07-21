import os
import sys
import logging

from django.apps import AppConfig

class UpdaterConfig(AppConfig):
    name = 'updater'

    def ready(self):
            from . import tasks
            print("Starting market thread...")
            logging.basicConfig(stream=sys.stdout,level=logging.DEBUG)
            if os.environ.get("RUN_MAIN",None) != 'true' and 'runserver' in sys.argv:
                logging.info("Starting market updater")
                tasks.start_scheduler()
                pass
