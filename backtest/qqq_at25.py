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
# endyear = 2006
# endmonth = 1
# endday = 1

start = dt.datetime(startyear, startmonth, startday)
end = dt.datetime.now()

# --------------------------------------------------------------------------------

# Import data
qqq = pdr.get_data_yahoo(stock, start, end)
krw = pdr.get_data_yahoo(currency, start, end)
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

buy_list = []
for x in range(len(df['year'].unique())):
    if df['year'].unique()[x] != end.year:
        year_df = df[df['year'] == df['year'].unique()[x]]
        remains=0
        for i in range(1,13):
            month_df = year_df[year_df['month'] == i]
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
            remains = total_dollar - (qqq_buy_quantity*qqq_price)

            # total list
            total_list = {
                'date' : current_date,
                'QQQ price' : qqq_price,
                'Dollar price' : dollar_price,
                'qqq_buy_quantity' : qqq_buy_quantity
            }
            buy_list.append(total_list)
    else:
        year_df = df[df["year"] == end.year]
        remains=0
        # We buy until previous month
        for j in range(df["month"].iloc[-1] - 1):
            # Make dataframe every month this year
            month_df = year_df[year_df['month'] == year_df['month'].unique()[j]]
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
            remains = total_dollar - (qqq_buy_quantity*qqq_price)

            # total list
            total_list = {
                'date' : current_date,
                'QQQ price' : qqq_price,
                'Dollar price' : dollar_price,
                'qqq_buy_quantity' : qqq_buy_quantity
            }
            buy_list.append(total_list)

# Save buy list csv file about QQQ Backtest Strategy        
qqq_buy_list = pd.DataFrame.from_dict(buy_list)
qqq_buy_list.to_csv("./backtest_result/qqq_buy_list_at25.csv", index=False)

# Total Revenue
QQQ_price = qqq_buy_list.iloc[0]["QQQ price"]
QQQ_quantity = qqq_buy_list.iloc[0]["qqq_buy_quantity"]
Dollar = qqq_buy_list.iloc[0]["Dollar price"]

QQQ_price1 = qqq_buy_list.iloc[100]["QQQ price"]
QQQ_quantity1 = qqq_buy_list.iloc[100]["qqq_buy_quantity"]
Dollar1 = qqq_buy_list.iloc[100]["Dollar price"]

print(QQQ_price*QQQ_quantity*Dollar + QQQ_price1*QQQ_quantity1*Dollar1)
print(QQQ_price1*(QQQ_quantity1 + QQQ_quantity)*Dollar1)
print((QQQ_price1*(QQQ_quantity1 + QQQ_quantity)*Dollar1/(QQQ_price*QQQ_quantity*Dollar + QQQ_price1*QQQ_quantity1*Dollar1)-1)*100)


    



