import pandas as pd
import numpy as np
import FinanceDataReader as fdr
from datetime import datetime as dt
import datetime
from pandas_datareader import data as pdr

startyear = 2006
startmonth = 1
startday = 1


stringdate = str(startday)+"/"+str(startmonth)+"/"+str(startyear)
string_formatter = "%d/%m/%Y"
startdate = dt.strptime(stringdate, string_formatter)
enddate = datetime.datetime.now()

etf_list = ['tqqq', 'qld', 'xle', 'gld', 'ief']
# merge_dataframe function을 사용하기 위해서는 뒤에가 더 길어야함.
# 오른쪽으로 가면서, 데이터가 짧아지면 데이터 잃어 버린다.

# Judge what is the cycle now?


def raw_dataframe(startdate):
    df = fdr.DataReader(['BAMLH0A0HYM2', 'DGS10', 'DGS2',
                        'T10Y2Y', 'T10Y3M'], data_source='fred', start=startdate)
    df['10_2year_log'] = np.log(df['DGS10']/df['DGS2'])
    df['high_yield_log'] = np.log(df['BAMLH0A0HYM2'])
    df.drop(['DGS10', 'DGS2', 'BAMLH0A0HYM2'], axis=1, inplace=True)

    now_x = round(df['high_yield_log'][-1], 2)
    now_y = round(df['10_2year_log'][-1], 2)
    return df, now_x, now_y

# SubPrime Mortgage Crisis 2007-11-01 ~ 2009-03-06
# Covid 19 2020-02-01 ~ 2020-03-23


def judge_cycle(df):
    df['cycle'] = 0
    df.loc[(df['high_yield_log'] > 1.5) & (
        df['10_2year_log'] < 1), 'cycle'] = 'crisis'
    df.loc[(df['high_yield_log'] > 1.5) & (
        df['10_2year_log'] > 1), 'cycle'] = 'explosion'
    df.loc[(df['high_yield_log'] < 1.5) & (
        df['10_2year_log'] > 1), 'cycle'] = 'growth'
    df.loc[(df['high_yield_log'] < 1.5) & (
        df['10_2year_log'] < 1), 'cycle'] = 'risk'
    return df


def judge_cycle2(df):
    df.reset_index(inplace=True)
    df["year"] = df["DATE"].dt.year
    df['cycle'] = 0
    x_max = df['high_yield_log'].max()
    for i in range(len(df)):
        x = df['high_yield_log'].iloc[i]
        y = df['10_2year_log'].iloc[i]
        if (y < 0) and (df['T10Y3M'].iloc[i] < 0):
            df['cycle'].iloc[i] = 'crisis'
    # print(df[df['high_yield_log'] == x_max], x_max)


df, now_x, now_y = raw_dataframe(startdate)

# cycle_df = judge_cycle(df)
# judge_cycle2(df)

# Collect Price Dataframe for each ETF
df_list = []
for x in range(len(etf_list)):
    etf = etf_list[x].upper()
    etf_df = pdr.get_data_yahoo(etf, startdate, enddate)[['Adj Close']]
    etf_df.rename(columns={'Adj Close': etf_list[x]}, inplace=True)
    df_list.append(etf_df)
# merge each dataframe

merge_df = pd.merge(df_list[0], df_list[1],
                    how='right', left_index=True, right_index=True)
if merge_df.iloc[0].isna().all():
    print("Error!")
else:
    for x in range(2, len(etf_list)):
        merge_df = pd.merge(merge_df, df_list[x],
                            how='right', left_index=True, right_index=True)

print(merge_df.head())
