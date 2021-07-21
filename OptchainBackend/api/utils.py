import bisect
import math
import re
from datetime import date, datetime, timedelta


def filterTimeList(lst:list,attr:str) -> list:
    '''
    This function takes a list or queryset, and based on conditionals,
    will strip out times. With '1Y' supplied, and a list of objects
    with 5m time increments, we shorten list to weekly datapoints, etc
    '''
    latest, oldest = getattr(lst[0],attr), getattr(lst[-1],attr)
    time_diff = (latest - oldest).days
    chk = {
        7: timedelta(minutes=30), 
        30: timedelta(hours=1), 
        90: timedelta(hours=3),
        365: timedelta(days=2),
        720: timedelta(weeks=1),
        1100: timedelta(weeks=4)
    }
    if time_diff <= 1:
        return lst

    c_keys = list(chk.keys())
    delta = chk[c_keys[bisect.bisect_left(c_keys,time_diff)]]
    res = [lst.pop(0)]
    prev = latest
    cur = prev - delta
    
    for x in lst:
        t = getattr(x,attr)
        if abs((t - cur)) <= delta/2:
            res.append(x)
            cur -= delta
        elif abs(prev-t) > delta*1.5:
            cur = t-delta
            res.append(x)

        prev = t
    return res


    


#Thanks to https://stackoverflow.com/questions/4628122/how-to-construct-a-timedelta-object-from-a-simple-string
def parse_time(time_str) -> timedelta:
    time_str = time_str.lower()

    regex = re.compile(r'((?P<hours>\d+?)h)?((?P<days>\d+?)d)?((?P<weeks>\d+?)wk)?((?P<months>\d+?)mo)?((?P<years>\d+?)y)?((?P<minutes>\d+?)m)?')
    extended_match = {
        'months': lambda x: x*4,
        'years': lambda x: x*52
    }

    if time_str == 'ytd':
        year_start = date(date.today().year,1,1)
        return date.today() - year_start



    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            if name in extended_match.keys():
                func = extended_match[name]

                time_params['weeks'] = func(int(param))
            else:
                time_params[name] = int(param)
    return timedelta(**time_params)



def parseBoolean(string):
    if type(string) == bool:
        return string
    response = None
    if string is 0 or string is None:
        response = False
    if string is 1:
        response = True
    if isinstance(string, str):
        if string.lower() in ["0", "no", "false"]:
            response = False
        if string.lower() in ["1", "yes", "true"]:
            response = True
    return response
