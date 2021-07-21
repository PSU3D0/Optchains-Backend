from yfinance.ticker import Ticker


msft = Ticker("MSFT")
msft.history(period="5d",interval="1h")