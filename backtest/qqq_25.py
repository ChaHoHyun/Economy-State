import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr

# Every month 1,000,000 won
money = 1000000
# NASDAQ INDEX ETF
stock = "QQQ"
# Dollar Exchange Rate
currency = 'KRW%3DX'

# Set BackTest Start-End date
startyear = 2006
startmonth = 1
startday = 1

start = dt.datetime(startyear, startmonth, startday)
now = dt.datetime.now()

# --------------------------------------------------------------------------------

# Import data
qqq = pdr.get_data_yahoo(stock, start, now)
krw = pdr.get_data_yahoo(currency, start, now)
# Setting Data-preprocessing
qqq.reset_index(inplace=True)
qqq["year"] = qqq["Date"].dt.year
qqq["month"] = qqq["Date"].dt.month
qqq["day"] = qqq["Date"].dt.day
# Drop Column
qqq = qqq.drop(['High', 'Low', 'Open', 'Close', 'Volume'], axis=1)
# Merge each data
df = pd.merge(qqq, krw["Adj Close"], how='left', on='Date')
# Change Column name
df.rename(columns = {'Adj Close_x':'qqq_price','Adj Close_y':'dollar'},inplace=True)

# --------------------------------------------------------------------------------

# BackTesting
# revision : How to 나머지 값을 total asset에 더해주고 추가적으로 더 사게 하는 법?

first_year = df[df['year'] == 2006]
buy_list = []
remains = 0
for i in range(1,13):
    month_df = first_year[first_year['month'] == i]
    # Current date
    current_date = month_df.iloc[-5]["Date"].strftime('%Y-%m-%d')
    # qqq Current Price
    qqq_price = round(month_df.iloc[-5]['qqq_price'],2)
    # dollar Current Price
    dollar_price = round(month_df.iloc[-5]['dollar'],2)

    # Error : QQQ has value, but No dollar in month_df
    x=0
    while pd.isnull(dollar_price):
        x += 1
        dollar_price = month_df.iloc[-5-x]['dollar']

    # Total dollar = total asset/current dollar
    total_dollar = money/dollar_price + remains
    # Buyable QQQ quantity
    qqq_buy_quantity = int(total_dollar/qqq_price)
    # remain dollar
    remain = total_dollar - (qqq_buy_quantity*qqq_price)
    print(qqq_price)
    print(remain)
    print(remains)
    buy_list.append({
        'date' : current_date,
        'QQQ price' : qqq_price,
        'Dollar price' : dollar_price,
        'qqq_buy_quantity' : qqq_buy_quantity
    })

    remains = remains + remain

# print(buy_list[0])



