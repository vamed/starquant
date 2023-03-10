from abc import abstractmethod
# 信号基类
class SignalBase():

    def __init__(self):
        pass

    # 匹配买入信息
    @abstractmethod
    def fit_buy(self, stock_indicator):
        ret = False
        return ret

    # 匹配卖出信息
    @abstractmethod
    def fit_sell(self, stock_indicator):
        ret = False
        return ret
