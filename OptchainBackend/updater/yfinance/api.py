from datetime import date, datetime
from pprint import pprint

import pandas as pd
from pandas import Timestamp
from requests import Session

import yfinance as yf
from yfinance.ticker import Ticker

from .utils import fixNans, validateDict

'''
This file contains all the functions that interface directly with the yahoo finance API
'''


def makeInteger(val,rounding=3) -> int:
    if type(val) == float:
        val = round(val,rounding)
        return int(val*100)
    return val


class InvalidTimeSpecifierError(Exception):
    pass


class YahooFinanceInterface():
    def __init__(self):
        self.hourly_requests = 2000
        self.tickers = {}
        self.session = Session()


    def _clear_tickers(self) -> None:
        self.tickers = {}

    def _get_ticker(self,symbol:str,cache=False) -> Ticker:

        if cache:
            ticker = self.tickers.get(symbol)

            if not ticker:
                ticker = yf.Ticker(symbol,self.session)
                self.tickers[symbol] = ticker
            return ticker
        else:
            return yf.Ticker(symbol,self.session)
    

    def getTickerData(self,ticker:str):
        ticker = self._get_ticker(ticker)
        try:
            data = ticker.info
        except KeyError:
            print("%s does not exist on yfinance API!" % ticker)
            return False

        d = {
            'Name': data['shortName'],
            'Ticker': ticker,
            'Category': data['sector']
        }
        #Until interface is up, only getting what we need
        return d



    def getStockHistory(self,ticker,period,interval):
        valid_periods = ('1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max')
        valid_intervals = ('1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo')

        if period not in valid_periods or interval not in valid_intervals:
            raise InvalidTimeSpecifierError("Invalid period or interval supplied")
        ticker = self._get_ticker(ticker)

        df = ticker.history(period,interval)
        dct = df.to_dict("index")

        return {k.to_pydatetime(): {i: j for i,j in v.items()} for k,v in dct.items() if validateDict(v)}



    def getStockOptionExpirations(self,ticker):
        return [datetime.strptime(date,"%Y-%m-%d") for date in self._get_ticker(ticker).options]


    def getOptionChain(self,ticker, date_obj):
        date_str = date.strftime(date_obj,"%Y-%m-%d")

        ticker = self._get_ticker(ticker)
        try:
            options = ticker.option_chain(date_str)
        except ValueError:
            #Weird Yfinance API bug makes this neccesary
            #Sometimes an expiration is given that is invalid
            return {}
        calls = options.calls.to_dict("records")
        puts = options.puts.to_dict("records")

        return {"Calls": calls, "Puts": puts}




if __name__ == "__main__":
    from pprint import pprint
    data = YahooFinanceInterface.getStockHistory("MMM","1mo","5m")

    i = 0
    for time, t_data in data.items():
        print(t_data)
        i+=1
        if i == 5:
            break
    #pprint(YahooFinanceInterface.getStockOptionExpirations("MSFT"))
