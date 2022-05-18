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


df, now_x, now_y = raw_dataframe(startdate)
cycle_df = judge_cycle(df)

# Collect Price Dataframe for each ETF
df_list = []
for x in range(len(etf_list)):
    etf = etf_list[x].upper()
    etf_df = np.array(pdr.get_data_yahoo(etf, startdate, enddate)['Adj Close'])
    etf_dict = {
        'ETF': etf,
        f'{etf}_close': etf_df
    }
    df_list.append(etf_dict)

nasdaq = pdr.get_data_yahoo('QQQ', startdate, enddate)[['Adj Close']]
nasdaq.rename(columns={'Adj Close': 'QQQ'}, inplace=True)
