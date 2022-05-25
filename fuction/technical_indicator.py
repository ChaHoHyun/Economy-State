import pandas as pd
import talib as ta
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_rsi(dataframe, rsi_day):
    dataframe['rsi'] = ta.RSI(dataframe["Adj Close"], rsi_day)
    return dataframe


def read():
    gc = gspread.service_account(
        filename="./client_secret_887022892602-celthn1l449fsrlg7jac5pgo8md5tfs0.apps.googleusercontent.com.json")
    sh = gc.open("dividends").workwheet("macquerie")
    print(sh.get('E3'))


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'my.json', scope)
gc = gspread.authorize(credentials)
