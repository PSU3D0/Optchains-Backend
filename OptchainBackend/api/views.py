import itertools
from datetime import date, datetime, timedelta
from pprint import pprint

import pytz
from django.db.models import Prefetch, Q
from django.http.response import Http404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from database.models import OptionsContract, Stock, StockPrice
from .pagination import StandardResultsSetPagination
from .serializers import *
from .utils import filterTimeList, parse_time, parseBoolean


class StockTickerList(ListAPIView):
    serializer_class = BaseStockSerializer
    queryset = Stock.objects.all()


class StockPriceList(ListAPIView):
    serializer_class = StockPriceSerializer


    def get_queryset(self):
        stock = self.kwargs.get("ticker",None)
        period = parse_time(self.request.query_params.get("period","1mo"))
        interval = parse_time(self.request.query_params.get("interval","5m"))

        stock_obj = Stock.objects.get(ticker=stock)

        try:
            from_date = StockPrice.objects.filter(stock=stock_obj).latest("time").time - period
            queryset = StockPrice.objects.filter(Q(Q(stock=stock_obj) & Q(time__gte=from_date)))
        except StockPrice.DoesNotExist:
            return []
        
        return reversed(filterTimeList(list(queryset),'time'))



class OptionsExpirations(APIView):
    def get(self,request,ticker,format=None):
        stock = Stock.objects.get(ticker=ticker)

        if parseBoolean(self.request.query_params.get("valid",True)):
            expirations = list(dict.fromkeys(stock.contracts.filter(expiration__gte=datetime.now())\
                .values_list("expiration",flat=True).order_by("expiration")))
        else:
            expirations = list(dict.fromkeys(stock.contracts\
                .values_list("expiration",flat=True).order_by("expiration")))

        return Response(expirations,content_type="json")
    

class OptionsSummary(ListAPIView):
    '''
    Returns summary data for options contracts from a given date
    If expiration is not provided, provides all
    '''
    serializer_class = OptionsContractSummarySerializer


    def get_queryset(self):
        ticker = self.kwargs.get("ticker",None)
        expiry = self.request.query_params.get("expiry",None)
        interest = self.request.query_params.get("interest",1)#Filter contracts to have non-zero open interest



        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            return []

        contracts = OptionsContract.objects.filter(stock=stock)
        if expiry:
            expiry = datetime.strptime(expiry,"%Y-%m-%d")
            return contracts.filter(expiration=expiry)
        
        return contracts
        

        
        


class OptionsPriceList(ListAPIView):
    serializer_class = OptionsPriceHistorySerializer
    pagination_class = StandardResultsSetPagination

    

    def get_queryset(self):
        ticker = self.kwargs.get("ticker",None)
        expiry = self.request.query_params.get("expiry",None)
        period = parse_time(self.request.query_params.get("period","1mo"))

        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            return []

        queryset = OptionsContract.objects.filter(stock=stock)



        if expiry:
            queryset = queryset.filter(expiration=datetime.strptime(expiry,"%Y-%m-%d").date())
        else:
            from_date = date.today() - period
            queryset = OptionsContract.objects.filter((Q(stock=stock) & Q(expiration__gte=from_date)))
        
        return queryset.order_by("expiration")


class OptionsPriceHistory(ListAPIView):
    serializer_class = OptionsPriceSerializer

    def get_queryset(self):
        contract = self.kwargs.get("contract",None)
        period = parse_time(self.request.query_params.get("period","1mo"))

        try:
            contract_obj = OptionsContract.objects.get(symbol=contract)
        except OptionsContract.DoesNotExist:
            return []
        
        from_date = date.today() - period
        queryset = OptionsContractPrice.objects.filter\
            (Q(Q(option=contract_obj) & Q(recorded__gte=from_date)))

        return queryset
