import logging
import threading
import gc
from datetime import datetime, time, timedelta
#from multiprocessing import Process, Queue
from time import sleep
from threading import Thread
from queue import Queue

#from queue import Queue
import holidays
from django.utils import timezone
from schedule import Scheduler

from .actions import *
from database.models import *
from .yfinance.utils import roundDelta




class UpdateCoordinator():
    def __init__(self,hourly_limit:int,worker_count=1):
        self.hourly_limit = hourly_limit
        self.worker_count = worker_count

        self.call_count = 0
        self.started = timezone.now()
        self.update_queue = None

        self.workers_running = False
        self.now = None


    def _checkResetTime(self):
        if timezone.now() > self.started + timedelta(hours=1):
            self.call_count = 0


    def start_workers(self):
        self.workers_running = True
        workers = [Thread(target=self.worker_pull) for _ in range(self.worker_count)]
        for t in workers:
            t.daemon = True
            print("Starting worker %s" % t)
            t.start()
    
    def worker_pull(self):
        while True:
            if self.update_queue.empty():
                if self.workers_running:
                    logging.info("Stock queue empty, task complete")
                    self.workers_running = False

            stock = self.update_queue.get()
            diff = roundDelta(self.now-stock.date_updated)
            downloadStockHistory(stock.ticker,diff,"5m")
            self.call_count += downloadOptionChainData(stock.ticker)

            self.call_count+=1

            if self.call_count > self.hourly_limit-10:
                print("\nApproaching hourly call limit. Canceling remaining")
                break


    def update(self,multi=False):
        self._checkResetTime()

        stocks = Stock.objects.all()
        self.now = timezone.now()

        if multi:
            if not self.update_queue:
                self.update_queue = Queue()

            logging.info("Starting stock-update job")
            for stock in stocks:
                self.update_queue.put(stock)
            logging.info("Loaded queue with stock list")
            
            if not self.workers_running:
                self.start_workers()
                logging.info("Started workers")
        else:
            for stock in stocks:
                cur = self.call_count
                diff = roundDelta(self.now-stock.date_updated)
                downloadStockHistory(stock.ticker,diff,"5m")
                self.call_count += downloadOptionChainData(stock.ticker)
                self.call_count+=1
                print("Added %s new datapoints for %s" % (self.call_count-cur,stock.ticker))
        
        gc.collect()




def start_market_update(updater,force=False):
    '''
    Checks to see if we are within market hours, if so,
    triggers standard update function
    '''
    start = timezone.localtime(timezone.now().replace(hour=14,minute=30,second=0,microsecond=0)).time()
    end = timezone.localtime(timezone.now().replace(hour=21,minute=0,second=0,microsecond=0)).time()
    now = timezone.localtime(timezone.now())
    now_time = now.time()
    if now.weekday() < 5:
        print("Checking market hours, current time is %s" % now_time)
        if start <= now_time <= end and now not in holidays.US():
            print("\nWithin market hours, starting scan at %s\n" % now)
            updater.update()
            return
    if force:
        updater.update()





def run_continuously(self, interval=1):
    """Continuously run, while executing pending jobs at each elapsed
    time interval.
    @return cease_continuous_run: threading.Event which can be set to
    cease continuous run.
    Please note that it is *intended behavior that run_continuously()
    does not run missed jobs*. For example, if you've registered a job
    that should run every minute and you set a continuous run interval
    of one hour then your job won't be run 60 times at each interval but
    only once.
    """

    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run

Scheduler.run_continuously = run_continuously



def start_scheduler():
    '''
    Called from apps.py to start scheduled tasks.
    '''
    start_time = timezone.localtime(timezone.now().replace(hour=14,minute=30,second=0,microsecond=0)).time().strftime("%X")
    end_time = timezone.localtime(timezone.now().replace(hour=21,minute=0,second=0,microsecond=0)).time().strftime("%X")

    updater = UpdateCoordinator(2000)
    
    print("Starting market update scheduler")
    scheduler = Scheduler()
    

    scheduler.every().day.at(start_time).do(start_market_update,updater,True)
    scheduler.every().day.at(end_time).do(start_market_update,updater,True)
    scheduler.every(60).minutes.do(start_market_update,updater)
    scheduler.run_continuously()
    start_market_update(updater,True)#Initial update
