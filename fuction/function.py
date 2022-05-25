import FinanceDataReader as fdr
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt
import talib as ta
import matplotlib.pyplot as plt
import numpy as np

api_key = '11f82ea0c8fa69832df775a90ae98bce5cf03db1'

now = dt.datetime.now()

sktelecom = '017670.KS'
maquerie = '088980.KS'


def get_stock_close(ticker, start, end):
    stock = pdr.get_data_yahoo(ticker, start, end)
    stock['Adj Close'] = round(stock['Adj Close'], 2)
    return stock[['Adj Close']]


def get_dividends(ticker, Dividend_count, start, end):
    stock_info = yf.Ticker(ticker)
    dividends = stock_info.dividends
    dividends_date = pd.to_datetime(dividends.index.values[-1])
    last_dividends_year = dividends_date.year
    a = dividends_date.strftime("%Y-%m-%d")
    if last_dividends_year == now.year:
        print(
            f"{ticker} \n배당락일 : {a}\n배당금 {last_dividends_year}원")
    else:
        print(f"{ticker} 올해 배당 누락")
    last_dividends = dividends[-1]
    close = get_stock_close(ticker, start, end)
    df = pd.merge(close, dividends, how='left',
                  left_index=True, right_index=True)
    df.fillna(method='ffill', inplace=True)
    df['dividends_rate'] = round(df['Dividends'] /
                                 df['Adj Close'] * 100 * Dividend_count, 2)
    df.dropna(axis=0, inplace=True)
    return df[['Adj Close', 'dividends_rate']], last_dividends


def get_percentile(series, percentile_value):
    series = series.dropna()
    result = round(np.percentile(series, percentile_value), 2)
    return result


skt_df, last_dividends = get_dividends(sktelecom, 4, 2022, now)
# skt_divrate_top10 = get_percentile(skt_df['dividends_rate'], 90)
# print(last_dividends, skt_divrate_top10)
# skt_df['dividends_rate'].plot()
# plt.show()

maquerie_df, last_dividends = get_dividends(maquerie, 2, 2018, now)
# print(maquerie_df.head(), last_dividends)
