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

etf_list = ['xle', 'qld', 'tqqq', 'gld', 'ief', 'sso', 'spy', 'qqq']

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


def find_sell_point(df):
    df['10_2year_log_1'] = df.loc[:, '10_2year_log'].shift(1)
    sell_date = df[(df['10_2year_log_1'] < 0) & (
        df['10_2year_log'] >= 0)]
    return sell_date


def judge_state(df):
    df.reset_index(inplace=True)
    df['year'] = df['DATE'].dt.year
    df_1st = df[df['year'] < 2019]
    df_2nd = df[df['year'] >= 2019]

    x_max = df_1st['high_yield_log'].max()
    y_max = df_1st['10_2year_log'].max()
    x_max2 = df_2nd['high_yield_log'].max()
    y_max2 = df_2nd['10_2year_log'].max()

    crisis_start = find_sell_point(df_1st).iloc[-1, 0]
    recovery_start = df_1st[df_1st['high_yield_log'] == x_max].iloc[0, 0]
    growth_start = df_1st[df_1st['10_2year_log'] == y_max].iloc[0, 0]
    risk_start = df_1st[(df_1st['10_2year_log'] < 1) & (df_1st['10_2year_log'] > 0.5) &
                        (df_1st['high_yield_log'] < 1.5)].iloc[0, 0]

    crisis_start_2nd = find_sell_point(df_2nd).iloc[0, 0]
    recovery_start2 = df_2nd[df_2nd['high_yield_log'] == x_max2].iloc[0, 0]
    growth_start2 = df_2nd[df_2nd['10_2year_log'] == y_max2].iloc[0, 0]
    risk_start2 = df_2nd[(df_2nd['10_2year_log'] < 1) & (df_2nd['10_2year_log'] > 0.5) &
                         (df_2nd['high_yield_log'] < 1.5)].iloc[0, 0]

    date_list = [crisis_start, recovery_start, growth_start, risk_start,
                 crisis_start_2nd, recovery_start2, growth_start2, risk_start2]
    cycle_list = ['risk1', 'crisis1', 'recovery1', 'growth1',
                  'risk2', 'crisis2', 'recovery2', 'growth2', 'risk3']
    index_list = [0]
    df['state'] = 0
    for i in range(len(date_list)):
        date_index = df[df['DATE'] == date_list[i]].index.values[0]
        index_list.append(date_index)
        df.loc[index_list[i]:index_list[i+1], 'state'] = cycle_list[i]
    df.loc[df['state'] == 0, 'state'] = 'risk3'
    df.set_index('DATE', inplace=True)
    return df, date_list

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


# # Excute all function
df, now_x, now_y = raw_dataframe(startdate)
df, date_list = judge_state(df)
new_etf_list = change_order_list(etf_list)
price_df = merge_all_price_df(new_etf_list)
merge_final = pd.merge(price_df, df[['state', 'year']],
                       how='left', left_index=True, right_index=True)
print(date_list)
merge_final.to_csv(
    f"./results/cycle/merge_final.csv", index=True)
