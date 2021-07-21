from django.db.models.base import Model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from database.models import *

'''
Serializers for database items
'''

class BaseStockSerializer(ModelSerializer):
    class Meta:
        model = Stock
        fields = ['name','ticker','category']


class StockPriceSerializer(ModelSerializer):
    class Meta:
        model = StockPrice
        exclude = ['id','stock']

class StockHistorySerializer(ModelSerializer):
    prices = StockPriceSerializer(many=True,read_only=True)
    class Meta:
        model = Stock
        fields = ['name','ticker','prices']


class OptionsPriceSerializer(ModelSerializer):
    class Meta:
        model = OptionsContractPrice
        exclude = ('id','implied_volatility','option')

class OptionsPriceHistorySerializer(ModelSerializer):
    #prices = OptionsPriceSerializer(many=True,read_only=True)
    class Meta:
        model = OptionsContract
        fields = ['symbol', 'expiration', 'strike',]
'''
class OptionsContractSummarySerializer(Serializer):
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        latest_data_rep = representation.pop('latest_data')
        for k,v in latest_data_rep.items():
            representation[k] = v
        return representation

    symbol = serializers.CharField(read_only=True)
    strike = serializers.DecimalField(8,2)
    expiration = serializers.DateField(read_only=True)
    contract_type = serializers.CharField(read_only=True)
    latest_data = serializers.ReadOnlyField()
'''

class OptionsContractSummarySerializer(ModelSerializer):
    
    latest_data = serializers.ReadOnlyField()
    def to_representation(self, instance):
        #https://stackoverflow.com/questions/44857249/how-can-i-flatten-a-foreignkey-object-with-django-rest-framework-gis
        representation = super().to_representation(instance)
        latest_data_rep = representation.pop('latest_data')
        for k,v in latest_data_rep.items():
            representation[k] = v
        return representation

    class Meta:
        model = OptionsContract
        fields = ['symbol','strike','expiration','latest_data','contract_type',]
        read_only_fields = fields
