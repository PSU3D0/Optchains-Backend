import math

def fixNan(val):
    if type(val) == float:
        if math.isnan(val):
            return None
    return val