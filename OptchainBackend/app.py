import sys
import os
import requests


def handler(event,context):
    print("Starting market update")

    print("Testing connection to Yfinance")
    address = 'http://query1.finance.yahoo.com/v8/'
    try:
        requests.get(address,timeout=5)
    except Exception as e:
        print("Couldn't connect to Yfinance!")
        print(e)
        return


    os.system("python updatelauncher.py force_option_update")