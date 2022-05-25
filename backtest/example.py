import FinanceDataReader as fdr
import pandas as pd
import OpenDartReader

data = pd.read_csv('./results/cycle/merge_final.csv')
data.set_index('Date', inplace=True)

# data['revenue_rate'] = 0
# data['current_value'] = 0
# data['mdd'] = 0


def buy_at_risk(data):
    sp500 = data['SPY']*0.2
    gold = data['GLD']*0.1
    ief = data['IEF']*0.2
    total = round(sp500 * gold * ief, 2)
    return total


data['total'] = 0
data['revenue_rate'] = 0
for x in range(len(data)):
    if (data['state'].iloc[x] == 'risk1'):
        sp500 = data['SPY'].iloc[x]*0.2
        gold = data['GLD'].iloc[x]*0.1
        ief = data['IEF'].iloc[x]*0.2
        data['total'].iloc[x] = round(sp500 * gold * ief, 2)

    elif (data['state'].iloc[x] == 'risk1'):
        pass
print(data.head())
