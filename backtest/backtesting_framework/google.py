import pandas as pd
import numpy as np
import yfinance as yf
from pandas_datareader import data as pdr
import datetime as dt
import talib as ta
from backtesting import Strategy, Backtest
from backtesting.lib import crossover

# NASDAQ INDEX ETF
stock = "GOOGL"
# Set BackTest Start-End date
startyear = 2018
startmonth = 1
startday = 1

start = dt.datetime(startyear, startmonth, startday)
now = dt.datetime.now()

google = pdr.get_data_yahoo(stock, start, now)


def rsi(df, period=14):
    rsi_series = ta.RSI(df["Adj Close"], period)
    return rsi_series


class rsi_below35(Strategy):
    def __init__(self):
        price = self.data.Close
        self.rsi = self.I(rsi(self))

    def next(self):
        if crossover(price, self.rsi):
            self.buy()


bt = Backtest(google, rsi_below35, commission=.002, exclusive_orders=True)
stats = bt.run()
bt.plot()

print(stats)
