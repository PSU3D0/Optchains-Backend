import csv
import os


from database.models import *
from .actions import downloadOptionChainData, downloadStockHistory
'''
Code that sets up the initial server, including populating DB, and other configurations
'''



def buildSPY():
    f = open(os.path.join(os.getcwd(),"updater","OEF_holdings.csv"),"r")

    reader = csv.reader(f)


    for row in reader:
        ticker = row[0].replace('"',"")
        stock,created = Stock.objects.get_or_create(
            ticker=ticker,
            name=row[1].title(),
            category=row[2].title(),
        )
        print("Building ticker: %s" % stock.ticker)
        downloadStockHistory(stock.ticker,"1mo","5m")
        downloadOptionChainData(stock.ticker)
        



if __name__ == "__main__":
    buildSPY()