import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
import talib as ta
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
# ------------------------------revision : def화----------------------------------
# --------------------------------------------------------------------------------
# Setting investment, start & end date

# Every condition(RSI<35) 1,000,000 won # ★★★★★★★★★★★★★★★★★★★★
money = 1000000
qqq = "QQQ"
qld = "QLD"
rsi = 35
strategy = f"{qld}_withRsi_Under35"

# Set BackTest Start-End date # ★★★★★★★★★★★★★★★★★★★★
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
# Data pre-processing + funtionalize-> RSI + krw


def preprocessing(df):
    df["rsi"] = ta.RSI(df["Adj Close"], 14)
    df["buy"] = 0
    df.loc[df["rsi"] < rsi, 'buy'] = 1
    # Merge qqq + krx, Drop/Rename columns, fill Nan value for krw
    merge_df = pd.merge(df, krw, how='left', left_index=True, right_index=True)
    merge_df.drop(['High', 'Low', 'Open', 'Close',
                  'Volume'], inplace=True, axis=1)
    merge_df.rename(columns={'Adj Close_x': 'qqq',
                             'Adj Close_y': 'krw'}, inplace=True)
    merge_df['krw'].fillna(method='ffill', inplace=True)
    # year, month value for buy at 25th
    merge_df.reset_index(inplace=True)
    merge_df["year"] = merge_df["Date"].dt.year
    merge_df["month"] = merge_df["Date"].dt.month
    return merge_df


merge_df = preprocessing(qld_df)  # ★★★★★★★★★★★★★★★★★★★★
# --------------------------------------------------------------------------------
# Backtesting
result_list = []
qqq_rsi = merge_df[merge_df['buy'] == 1]
remains = 0
for x in range(len(qqq_rsi)):
    current_date = qqq_rsi.iloc[x, 0].strftime('%Y-%m-%d')
    qqq_price = round(qqq_rsi.iloc[x, 1], 2)  # 35.26
    krw_price = round(qqq_rsi.iloc[x, 4], 2)  # 916.12
    total_dollar = round(money/krw_price, 2) + remains  # 1091.56
    buy_quantity = int(total_dollar/qqq_price)  # 30
    remains = round(total_dollar - (buy_quantity*qqq_price), 2)

    total_list = {
        'date': current_date,
        'qqq_price': qqq_price,
        'krw_price': krw_price,
        'qqq_buy_quantity': buy_quantity
    }
    result_list.append(total_list)

qqq_buy_list = pd.DataFrame.from_dict(result_list)
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

mdd_min = qqq_buy_list['mdd'].min()
mdd_now = qqq_buy_list['mdd'].iloc[-1]
# --------------------------------------------------------------------------------
# Result and Save .txt file
txt_file = open(
    f"./results/{strategy}_results.txt", "w", encoding='utf8')
print("-"*50, file=txt_file)
print(
    f"Total Investment Price {format(investment_from_now, ',')} won", file=txt_file)
print(f"How many times buy? {len(qqq_buy_list)}th", file=txt_file)
print(
    f"Average Invest price {format(int(investment_from_now/len(qqq_buy_list)), ',')} won", file=txt_file)
print(
    f"Current Valuation Price {format(int(current_total_valuation), ',')} won", file=txt_file)
print("-"*50, file=txt_file)
print(f"MDD (Max) : {mdd_min} %", file=txt_file)
print(f"MDD (Now) : {mdd_now} %", file=txt_file)
print(
    f"Revenue rate (Max) : {qqq_buy_list['revenue_rate'].max()} %", file=txt_file)
print(
    f"Revenue rate (Now) : {qqq_buy_list['revenue_rate'].iloc[-1]} %", file=txt_file)
print("-"*50, file=txt_file)
# --------------------------------------------------------------------------------
# Save qqq_buy_list by CSV file
qqq_buy_list.drop(['total', 'current_value'], axis=1, inplace=True)
qqq_buy_list.set_index(keys=qqq_buy_list['date'], inplace=True, drop=True)
qqq_buy_list.to_csv(
    f"./results/{strategy}_buy_list_at25.csv", index=False)
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
plt.title(f'Buy {strategy}', fontsize=25, pad=25, weight='bold')

plt.savefig(f'./results/{strategy}_backtest_result')
# qqq_buy_list.plot(style='candlestick', barup='red',
#                   bardown='blue', xtight=True, ytight=True, grid=True)
plt.show()
