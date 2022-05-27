import FinanceDataReader as fdr
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt
import talib as ta
import matplotlib.pyplot as plt
import numpy as np

spreadsheet_key = "spreadsheet_key"

now = dt.datetime.now()
last_year = dt.datetime.now().year - 1

sktelecom = '017670.KS'
maquerie = '088980.KS'
ktng = '033780.KS'


def get_stock_close(ticker, start, end):
    stock = pdr.get_data_yahoo(ticker, start, end)
    stock['Adj Close'] = round(stock['Adj Close'], 2)
    return stock[['Adj Close']]


def get_dividends(ticker, Dividend_count, start, end):
    stock_info = yf.Ticker(ticker)
    dividends = stock_info.dividends
    last_dividends = dividends[-1]
    dividends_date = pd.to_datetime(dividends.index.values[-1])
    last_dividends_year = dividends_date.year
    if last_dividends_year >= last_year:
        ex_dividend_date = dividends_date.strftime("%Y-%m-%d")
        print(
            f"{ticker} \n배당락일 : {ex_dividend_date}\n배당금 {last_dividends}원")
    else:
        print(f"Use read_spreadsheet fuction for load dividends {ticker}")
    close = get_stock_close(ticker, start, end)
    df = pd.merge(close, dividends, how='left',
                  left_index=True, right_index=True)
    df.fillna(method='ffill', inplace=True)
    df['dividends_rate'] = round(df['Dividends'] /
                                 df['Adj Close'] * 100 * Dividend_count, 2)
    df.dropna(axis=0, inplace=True)
    return df[['Adj Close', 'dividends_rate']], last_dividends


def get_percentile(stock_df, percentile_value):
    series = stock_df['dividends_rate']
    series = series.dropna()
    result = round(np.percentile(series, percentile_value), 2)
    return result


def read_spreadsheet(spreadsheet_key, worksheet_name, table_range):
    # JSON Key File Path
    json_key_path = '/mnt/d/my.json'
    gc = gspread.service_account(filename=json_key_path)
    # Open Google Spread Sheet by Key
    doc = gc.open_by_key(spreadsheet_key)
    sheet = doc.worksheet(worksheet_name)
    range_list = sheet.range(table_range)
    value_list = sheet.get(table_range)
    df = pd.DataFrame(value_list[1:], columns=value_list[0])
    return df


def view_div_chart(stock_df):
    last_divrate = stock_df['dividends_rate'].iloc[-1]
    divrate_top10 = get_percentile(stock_df, 90)
    plt.figure(figsize=(10, 10))
    plt.axhline(last_divrate, 0, 1, color='blue', linestyle='--', linewidth=2)
    plt.axhline(divrate_top10, 0, 1, color='red',
                linestyle='--', linewidth=2)
    stock_df['dividends_rate'].plot()
    plt.show()


# skt_df, last_dividends = get_dividends(sktelecom, 4, 2022, now)
# skt_divrate_top10 = get_percentile(skt_df, 90)
# print(last_dividends, skt_divrate_top10)


# maquerie_df, last_dividends = get_dividends(maquerie, 2, 2018, now)
# print(maquerie_df.head(), last_dividends)

# ktng_df, last_dividends = get_dividends(ktng, 1, 2008, now)
# ktng_divrate_top10 = get_percentile(ktng_df, 90)
# print(last_dividends, ktng_divrate_top10, ktng_df['dividends_rate'].iloc[-1])
