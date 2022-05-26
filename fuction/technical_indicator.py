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


json_key_path = '/mnt/d/my.json'  # JSON Key File Path

gc = gspread.service_account(filename=json_key_path)

spreadsheet_key = "spreadsheet_key"
doc = gc.open_by_key(spreadsheet_key)

sheet = doc.worksheet('macquerie')

list_of_lists = sheet.get_all_values()
value_a1 = sheet.get('E3')
list_of_dicts = sheet.get_all_records()
