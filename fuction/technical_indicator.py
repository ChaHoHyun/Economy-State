import pandas as pd
import talib as ta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

spreadsheet_key = "1knsK04P6nixvkFcUpcS407HcGpMfisir6FdVwdpuUX4"


def get_rsi(dataframe, rsi_day):
    dataframe['rsi'] = ta.RSI(dataframe["Adj Close"], rsi_day)
    return dataframe
