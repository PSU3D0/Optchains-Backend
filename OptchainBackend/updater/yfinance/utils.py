import math
from bisect import bisect_left
from datetime import timedelta


def validateDict(d:dict,)-> bool:
    '''
    The Yfinance API will occasionally give us float('NaN') values.
    Obviously we will reject these. This function provides as such
    '''
    for value in d.values():
        if math.isnan(value):
            return False
    return True

def roundDelta(time: timedelta)-> str:
    roundings = {
        1: "1d",
        5: "5d",
        30: "1mo",
        90: "3mo",
        180: "6mo",
        365: "1y",
    }
    keys = list(roundings.keys())
    return roundings[keys[bisect_left(keys,time.days)]]

def fixNans(lst:list) -> list:

    for data in lst:
        for k,val in data.items():
            if type(val) == float:
                if math.isnan(val):
                    data[k] = None
    return lst
