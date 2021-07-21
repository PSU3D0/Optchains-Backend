from datetime import datetime
from django.core.checks.messages import Error
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property

from django.db.models import JSONField

# Create your models here.



class Stock(models.Model):
    name = models.CharField(max_length=50)
    ticker = models.CharField(max_length=6,db_index=True)
    category = models.CharField(max_length=75)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return '{} - {}'.format(self.name,self.ticker)

    @property
    def contracts(self):
        return self.contracts.filter(expiration__gte=datetime.now())


class StockPrice(models.Model):
    stock = models.ForeignKey(Stock,on_delete=models.CASCADE,related_name="prices")
    time = models.DateTimeField(db_index=True)
    open = models.DecimalField(max_digits=8,decimal_places=2)
    high = models.DecimalField(max_digits=8,decimal_places=2)
    low = models.DecimalField(max_digits=8,decimal_places=2)
    close = models.DecimalField(max_digits=8,decimal_places=2)
    volume = models.PositiveIntegerField()

    class Meta:
        ordering = ['-time']


    def __str__(self) -> str:
        return self.stock.name + datetime.strftime(self.time,"%c")


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        #This updates stock when new history is added
        self.stock.date_updated = self.time
        self.stock.save()




class OptionsContractPrice(models.Model):
    option = models.ForeignKey("OptionsContract",on_delete=models.CASCADE,related_name="prices")

    last_price = models.DecimalField(max_digits=8,decimal_places=2)
    bid = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    ask = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    volume = models.PositiveIntegerField(blank=True,null=True)
    open_interest = models.PositiveIntegerField(blank=True,null=True)
    implied_volatility = models.DecimalField(max_digits=7,decimal_places=2,null=True,blank=True)

    last_trade = models.DateTimeField()
    recorded = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = '-recorded'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.option.latest_data = {
            'last_price': self.last_price,
            'bid': self.bid,
            'ask': self.ask,
            'volume': self.volume,
            'open_interest': self.open_interest
        }

            self.option.save()
        
        return super().save(*args,**kwargs)

class OptionsContract(models.Model):
    '''
    Represents a single options contract
    '''
    stock = models.ForeignKey(Stock,on_delete=models.CASCADE,related_name="contracts")
    symbol = models.CharField(max_length=25,db_index=True)
    expiration = models.DateField()
    strike = models.DecimalField(max_digits=8,decimal_places=2)#Stores value in cents
    contract_type = models.CharField(max_length=1,choices=[("C","Call"),("P","Put")])

    latest_data = JSONField(null=True)

    class Meta:
        ordering = ['-strike']


    def __str__(self) -> str:
        return self.symbol



