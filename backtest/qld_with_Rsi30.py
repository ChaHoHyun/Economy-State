import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
import talib as ta
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------------------------------------
# Setting investment, start & end date

# Every condition(RSI<35) 1,000,000 won
money = 1000000
qqq = "QQQ"
qld = "QLD"
rsi = 35

# Set BackTest Start-End date
startyear = 2006
startmonth = 1
startday = 1

start = dt.datetime(startyear, startmonth, startday)
end = dt.datetime.now()

# --------------------------------------------------------------------------------
# Import QQQ, QLD & KRW Data
qqq_df = pdr.get_data_yahoo(qqq, start, end)
qld_df = pdr.get_data_yahoo(qld, start, end)
krw = pdr.get_data_yahoo("KRW%3DX", start, end)[["Adj Close"]]
# --------------------------------------------------------------------------------
# Data pre-processing
# qqq -> RSI
qqq_df["rsi"] = ta.RSI(qqq_df["Adj Close"], 14)
qqq_df["buy"] = 0
qqq_df.loc[qqq_df["rsi"] < rsi, 'buy'] = 1
# Merge qqq + krx, Drop/Rename columns, fill Nan value for krw
qqq_krw = pd.merge(qqq_df, krw, how='left', left_index=True, right_index=True)
qqq_krw.drop(['High', 'Low', 'Open', 'Close', 'Volume'], inplace=True, axis=1)
qqq_krw.rename(columns={'Adj Close_x': 'qqq',
               'Adj Close_y': 'krw'}, inplace=True)
qqq_krw['krw'].fillna(method='ffill', inplace=True)
# year, month value for buy at 25th
qqq_krw.reset_index(inplace=True)
qqq_krw["year"] = qqq_krw["Date"].dt.year
qqq_krw["month"] = qqq_krw["Date"].dt.month

# --------------------------------------------------------------------------------
# Backtesting
result_list = []
# year_list = qqq_krw["year"].unique()
# for i in range(len(year_list)):
#     year_df = qqq_krw[qqq_krw["year"] == year_list[i]]
#     month_list = year_df['month'].unique()
#     for j in range(len(month_list)):
#         month_df = year_df[year_df['month'] == month_list[j]]
#         current_date = month_df.iloc[-5]["Date"].strftime('%Y-%m-%d')
qqq_rsi = qqq_krw[qqq_krw['buy'] == 1]
# qqq_rsi["quatity"] = 0
# qqq_rsi['total'] = 0
# qqq_rsi['revenue_rate'] = 0
# qqq_rsi['current_value'] = 0
# qqq_rsi['mdd'] = 0
# for i in range(len(qqq_rsi)):
#     current_date = qqq_rsi['Date'].iloc[i].strftime('%Y-%m-%d')
#     # qqq Current Price
#     qqq_price = round(qqq_rsi['qqq'].iloc[i], 2)
#     # dollar Current Price
#     dollar_price = round(qqq_rsi['krw'].iloc[i], 2)
#     qqq_rsi["quatity"].iloc[i] = int((money/dollar_price)/qqq_price)
#     # qqq_rsi['total'].iloc[i] = qqq_buy_quatity*qqq_price*dollar_price
#     # total_quatity =
#     # qqq_rsi['revenue_rate'].iloc[i] = qqq_buy_quatity*qqq_price*dollar_price

print(qqq_rsi.head())

# qqq_krw.set_index('Date', inplace=True)
