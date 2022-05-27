import pandas as pd
import talib as ta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from function import get_stock_close

ticker = 'qqq'
start = 2020
end = 2021
sma_list = [5, 20, 120]


def get_rsi(dataframe, rsi_day):
    dataframe['rsi'] = ta.RSI(dataframe["Adj Close"], rsi_day)
    return dataframe


def get_sma(dataframe, sma_day):
    dataframe['sma_'+str(sma_day)] = ta.SMA(dataframe["Adj Close"], sma_day)
    return dataframe


def get_macd(dataframe, number1, number2, number3):
    dataframe['macd'] = ta.MACD(
        dataframe["Adj Close"], number1, number2, number3)
    return dataframe


apple = get_stock_close(ticker, start, end)
print(get_sma(apple, 5))
