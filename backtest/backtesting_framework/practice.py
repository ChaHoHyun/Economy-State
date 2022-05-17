# Backtest : implement Backtest with our Strategy
# Strategy : Define our trading logic where do we buy where do we sell (Make Strategy)
from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import talib as ta
# it's very useful when we use crossover strategies
from backtesting.lib import crossover


class Rsi(Strategy):

    upper_bound = 70
    lower_bound = 30
    rsi_window = 14

    def init(self):
        # 이 함수는 객체가 생성되자마자 호출되며 한 번만 실행됩니다.
        # 기술 지표와 같이 백테스트 전에 미리 계산할 수 있는 모든 것을 여기에 입력해야 합니다.
        # 이 I기능은 backtesting.py 생태계 내에서 지표를 구축할 수 있게 해주기 때문에 살펴볼 가치가 있습니다.
        self.rsi = self.I(ta.RSI, self.data.Close, self.rsi_window)
        # I는 우리가 어떻게 Indicator를 설정하는지 정하는 것
        # I(function : Calculate Indicator Values, data를 전달(Close, Open, Volume 등), time window)

    def next(self):  # Traiding Logic (Pre-Calculate all of value)
        # next백테스트가 진행됨에 따라 모든 candle에서 호출됩니다.
        # candle open 시간에 그곳에 있었다면 당신의 논리는 어떤 모습이었을까요?
        # 우리의 경우 rsi가 우리보다 높은지 확인합니다 upper_bound.
        # 그것이 우리가 가지고있는 모든 위치에 가깝다면 (롱 또는 숏).
        # 그렇지 않으면 아래 lower_bound에 있는지 확인하십시오.
        # 이 경우 자산을 최대한 많이 구매해야 합니다.
        # backtesting.py주식의 정수만 구매 한다는 점에 유의하십시오.

        # next function은 모든 candle data를 하나하나 지나가면서, 매수/매도 기준을 계산하고 다음 candle 어디서 구매 해야하는지 정한다.
        if crossover(self.rsi, self.upper_bound):
            # crossover(first series, second series)
            # first series > second series = True => sell everything
            self.position.close()

        elif crossover(self.lower_bound, self.rsi):
            self.buy()


# Run backtesting
# (dataset, Strategy Class, cash, comission etc.)
bt = Backtest(GOOG, Rsi, cash=10_000)
# Optimize 'Sharp Ratio' Our strategy
stats = bt.optimize(
    upper_bound=range(50, 85, 5),
    lower_bound=range(10, 45, 5),
    rsi_window=range(10, 30, 2),
    maximize='Sharpe Ratio',  # Definition sharpe ratio : http://fnwiki.org/sharpe_ratio/
    constraint=100
)
# Express output stats about our strategy
print(stats)

# bt.plot(filename='examples/plot.html')
