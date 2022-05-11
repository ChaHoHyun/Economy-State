import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr

# Figure Setting
# plt.rcParams["axes.grid"] = True
plt.rcParams["figure.figsize"] = (15, 10)

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
df.rename(columns={'Adj Close_x': 'qqq_price',
          'Adj Close_y': 'dollar'}, inplace=True)
# --------------------------------------------------------------------------------
# BackTesting

buy_list = []
for x in range(len(df['year'].unique())):
    if df['year'].unique()[x] != end.year:
        year_df = df[df['year'] == df['year'].unique()[x]]
        remains = 0
        for i in range(1, 13):
            month_df = year_df[year_df['month'] == i]
            # Current date
            current_date = month_df.iloc[-5]["Date"].strftime('%Y-%m-%d')
            # qqq Current Price
            qqq_price = round(month_df.iloc[-5]['qqq_price'], 2)
            # dollar Current Price
            dollar_price = round(month_df.iloc[-5]['dollar'], 2)

            # Error : QQQ has value, but No dollar in month_df
            x = 0
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
                'date': current_date,
                'QQQ price': qqq_price,
                'Dollar price': dollar_price,
                'qqq_buy_quantity': qqq_buy_quantity
            }
            buy_list.append(total_list)
    else:
        year_df = df[df["year"] == end.year]
        remains = 0
        # We buy until previous month
        for j in range(df["month"].iloc[-1] - 1):
            # Make dataframe every month this year
            month_df = year_df[year_df['month']
                               == year_df['month'].unique()[j]]
            current_date = month_df.iloc[-5]["Date"].strftime('%Y-%m-%d')
            # qqq Current Price
            qqq_price = round(month_df.iloc[-5]['qqq_price'], 2)
            # dollar Current Price
            dollar_price = round(month_df.iloc[-5]['dollar'], 2)

            # Error : QQQ has value, but No dollar in month_df
            x = 0
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
                'date': current_date,
                'QQQ price': qqq_price,
                'Dollar price': dollar_price,
                'qqq_buy_quantity': qqq_buy_quantity
            }
            buy_list.append(total_list)

# Convert buy list csv file about QQQ Backtest Strategy
qqq_buy_list = pd.DataFrame.from_dict(buy_list)
# --------------------------------------------------------------------------------
# Revenue & MDD
# total = QQQ price x Dollar price x qqq_buy_quantity
qqq_buy_list['total'] = 0
qqq_buy_list['revenue_rate'] = 0
qqq_buy_list['current_value'] = 0
qqq_buy_list['mdd'] = 0
for i in range(len(qqq_buy_list)):
    qqq_buy_list.iloc[i, 4] = int(qqq_buy_list.iloc[i, 1] *
                                  qqq_buy_list.iloc[i, 2] * qqq_buy_list.iloc[i, 3])
    investment_from_now = qqq_buy_list.iloc[0:(i+1), 4].sum()
    current_total_valuation = qqq_buy_list.iloc[i, 1] * \
        qqq_buy_list.iloc[0:i+1, 3].sum() * qqq_buy_list.iloc[i, 2]
    qqq_buy_list['revenue_rate'].iloc[i] = round(((current_total_valuation /
                                                  investment_from_now)-1)*100, 2)

    current_value = round(qqq_buy_list.iloc[i, 1] * qqq_buy_list.iloc[i, 2], 2)
    qqq_buy_list['current_value'].iloc[i] = current_value
    max_value = qqq_buy_list.iloc[0:(i+1), 6].max()
    qqq_buy_list['mdd'].iloc[i] = round(
        (qqq_buy_list['current_value'].iloc[i] - max_value)/max_value*100, 2)

# --------------------------------------------------------------------------------
# Result and Save .txr file
mdd_min = qqq_buy_list['mdd'].min()
mdd_now = qqq_buy_list['mdd'].iloc[-1]

ticker = stock.lower()
txt_file = open(
    f"./backtest_result/{ticker}_results.txt", "w", encoding='utf8')
print("-"*50, file=txt_file)
print(
    f"Total Investment Price {format(investment_from_now, ',')} won", file=txt_file)
print(f"How many times buy? {len(qqq_buy_list)}th", file=txt_file)
print(
    f"Average Invest price {format(int(investment_from_now/len(qqq_buy_list)), ',')} won", file=txt_file)
print(
    f"Current Valuation Price {format(current_total_valuation, ',')} won", file=txt_file)
print("-"*50, file=txt_file)
print(f"MDD (Max) : {mdd_min} %", file=txt_file)
print(f"MDD (Now) : {mdd_now} %", file=txt_file)
print(
    f"Revenue rate (Max) : {qqq_buy_list['revenue_rate'].max()} %", file=txt_file)
print(
    f"Revenue rate (Now) : {qqq_buy_list['revenue_rate'].iloc[-1]} won", file=txt_file)
print("-"*50, file=txt_file)

# --------------------------------------------------------------------------------
# Save qqq_buy_list by CSV file
qqq_buy_list.drop(['total', 'current_value'], axis=1, inplace=True)
qqq_buy_list.set_index(keys=qqq_buy_list['date'], inplace=True, drop=True)
qqq_buy_list.to_csv(
    f"./backtest_result/{ticker}_buy_list_at25.csv", index=False)
# --------------------------------------------------------------------------------
# Visualization
fig, ax1 = plt.subplots()
ax1 = qqq_buy_list['revenue_rate'].plot(
    color='blue', alpha=0.3, legend='Revenue Rate (%)')
ax2 = ax1.twinx()
ax2 = qqq_buy_list['mdd'].plot(
    color='red', alpha=0.3, legend='MDD Rate (%)')

ax1.fill_between(qqq_buy_list.index, qqq_buy_list['revenue_rate'], alpha=0.2)
ax2.fill_between(qqq_buy_list.index,
                 qqq_buy_list['mdd'], alpha=0.2, color='red')

ax1.set_xlabel('Date', fontsize=20, labelpad=15, weight='bold')
ax1.set_ylabel('Revenue Rate (%)', fontsize=20, labelpad=15)
ax2.set_ylabel('MDD Rate (%)', fontsize=20, labelpad=15)

ax1.axhline(qqq_buy_list['revenue_rate'].iloc[-1], 0, 1,
            color='blue', linestyle='--', linewidth=1, alpha=0.5)
ax2.axhline(mdd_now, 0, 1, color='red', linestyle='--', linewidth=1, alpha=0.5)

ax1.set_xlim(qqq_buy_list.index[0], qqq_buy_list.index[-1])
ax1.set_ylim(0, qqq_buy_list['revenue_rate'].max())
ax2.set_ylim(mdd_min*2, 0)

ax1.legend(loc='lower left', fontsize=12)
ax2.legend(loc='upper right', fontsize=12)
export_now = f"NOW\nMDD : {mdd_now}%\nRevenue : {qqq_buy_list['revenue_rate'].iloc[-1]}%"
ax2.text(17, -37, export_now, fontsize=10, color="black",
         verticalalignment='top', horizontalalignment='center',
         bbox={'facecolor': 'whitesmoke', 'pad': 10})
plt.title(f'Buy {stock} always at 25th', fontsize=25, pad=25, weight='bold')

plt.savefig(f'./backtest_result/{ticker}_backtest_result')
# qqq_buy_list.plot(style='candlestick', barup='red',
#                   bardown='blue', xtight=True, ytight=True, grid=True)
plt.show()
