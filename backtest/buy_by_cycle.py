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

etf_list = ['xle', 'qld', 'tqqq', 'gld', 'ief']

# change_list_order


def change_order_list(etf_list):
    etf_order = []
    for x in range(len(etf_list)):
        etf = etf_list[x].upper()
        etf_df = pdr.get_data_yahoo(etf, startdate, enddate)[['Adj Close']]
        etf_order.append({
            "etf": etf,
            "length": len(etf_df)
        })
    order = pd.DataFrame.from_dict(etf_order)
    new_order = order.sort_values('length')['etf'].tolist()
    return new_order


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


def judge_state(df, now_x, now_y):
    df.reset_index(inplace=True)
    df['judgement'] = 0
    df['year'] = df['DATE'].dt.year
    for i in range(len(df)):
        x = df.iloc[i, 4]
        y = df.iloc[i, 3]
        if y < 0:
            df['judgement'].iloc[i] = 'risk'
        if (x > 1.5) and (y < 1):
            df['judgement'].iloc[i] = 'crisis'

    # year_list = df['year'].unique()
    # for x in range(len(year_list)):
    #     every_df = df[df['year'] == year_list[x]]
    #     if len(every_df[every_df['judgement'] == 'crisis']) < 3:
    #         print(every_df[every_df['judgement'] == 'crisis'].index.values)

    print(df['judgement'].unique())


# Import Price Dataframe for each ETF


def merge_all_price_df(etf_list):
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
    return merge_df


def backtesting(merge_final):
    for i in range(len(merge_final['cycle'].unique())):
        cycle_list = merge_final['cycle'].unique()[i]
        # print(merge_final[merge_final['cycle'] == cycle_list[i]].iloc[0])


# # Excute all function
df, now_x, now_y = raw_dataframe(startdate)
judge_state(df, now_x, now_y)
# new_etf_list = change_order_list(etf_list)
# price_df = merge_all_price_df(new_etf_list)
# cycle_df = judge_cycle(df)
# merge_final = pd.merge(price_df, cycle_df['cycle'],
#                        how='left', left_index=True, right_index=True)
# backtesting(merge_final)
