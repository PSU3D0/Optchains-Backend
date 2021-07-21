import logging
from typing import Union
from decimal import Decimal

from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.apps import apps

from yfinance import tickers

from database.models import OptionsContract, OptionsContractPrice, Stock, StockPrice

from .utils import fixNan




if settings.API_PROVIDER == 'yfinance':
    from .yfinance.api import YahooFinanceInterface
    API = YahooFinanceInterface()



def downloadTicker(ticker:str):
    '''
    We get ticker data from API and load it
    '''

    ticker_data = API.getTickerData(ticker)

    if not ticker_data:
        return False

    
    obj,created = Stock.objects.get_or_create(
        name=ticker_data['Name'],
        ticker=ticker,
        category=ticker_data['Category'],
    )

    logging.info("Created object %s" % obj)

    if created:
        print("%s object was created" % ticker)

    return obj


def downloadOptionChainData(ticker:str):
    '''
    Here we iterate through the entire options chain, adding data
    as we go
    '''

    import time

    stock_obj = Stock.objects.get(ticker=ticker)

    contracts = set(OptionsContract.objects.filter(stock=stock_obj)\
        .values_list("symbol",flat=True))
    contract_prices = set(OptionsContractPrice.objects.filter(Q(option__stock=stock_obj))\
        .values_list("option__symbol","last_trade","bid"))
    start = time.time()
    data = [(expiry,API.getOptionChain(ticker,expiry)) for expiry in API.getStockOptionExpirations(ticker)]
    c_count = 0
    i = 0

    for expiry, chains in data:
        for key,chain in chains.items():
            if key == 'Calls': con_type = 'C'
            else: con_type = 'P'
            for data in chain:
                contract_symbol = data['contractSymbol']

                if not contract_symbol in contracts:
                    contract_obj = OptionsContract.objects.create(
                        stock=stock_obj,
                        symbol=contract_symbol,
                        expiration=expiry,
                        strike=data['strike'],
                        contract_type=con_type
                    )
                    c_count +=1
                else:
                    contract_obj = OptionsContract.objects.get(symbol=contract_symbol)
                localized_time = timezone.make_aware(data['lastTradeDate'].to_pydatetime()\
                    .replace(second=0,microsecond=0))
                
                bid = fixNan(data['bid'])
                d_bid = None if not bid else Decimal(str(bid))

                if (contract_symbol,localized_time,d_bid) not in contract_prices:
                    pricepoint = OptionsContractPrice.objects.create(
                        option = contract_obj,
                        last_price = fixNan(data['lastPrice']),
                        bid = bid,
                        ask = fixNan(data['ask']),
                        volume = fixNan(data['volume']),
                        last_trade = localized_time,
                    )
                    i+=1
    print("Added %s new contracts for %s" % (c_count,stock_obj.ticker))
    print("Added %s new options data points for %s" % (i,stock_obj.ticker))
    print(f"\nTook {time.time()-start:.2f} seconds total")
    return 10





def downloadStockHistory(ticker: str,period:str,interval:str):
    '''
    Main function used to get history from whichever API is in use
    and make new database records, checking existing
    '''
    data = API.getStockHistory(ticker,period,interval)

    stock = Stock.objects.get(ticker=ticker)

    #We do it this way becasue we know that for each stock, datetime is unique
    datetimes = set(StockPrice.objects.filter(stock=stock).datetimes("time","minute"))
    i = 0
    for time,t_data in data.items():
        if time not in datetimes:
            StockPrice.objects.create(
                stock=stock,
                time=time,
                open=t_data['Open'],
                high=t_data['High'],
                low=t_data['Low'],
                close=t_data['Close'],
                volume=t_data['Volume'],
            )
            i+=1
            datetimes.add(time)
    if i > 0:
        #print("Grabbed %s new datapoints for %s" % (i,stock))
        logging.info("Grabbed %s new datapoints for %s" % (i,stock))
        return True
    return False




