from abc import abstractmethod
from quant.signals.signalbase import SignalBase

# macd
class MacdSignal(SignalBase):

    def __init__(self):
        self.name="MacdSignal"

    # 匹配买入信息
    # @classmethod
    def fit_buy(self, stock_indicator):
        ret = False
        indicator=''

        if (stock_indicator.pre_dif < stock_indicator.pre_dea) and (stock_indicator.dif >= stock_indicator.dea):
            indicator="pre_dif:{},pre_dif:{},dif:{},dea:{}".format(stock_indicator.pre_dif,
                                                                        stock_indicator.pre_dea, stock_indicator.dif,
                                                                        stock_indicator.dea)
            ret=True
        return (ret,self.name,indicator)

    # 匹配卖出信息
    # @abstractmethod
    def fit_sell(self, stock_indicator):
        ret = False
        indicator = ''
        if(stock_indicator.pre_dif > stock_indicator.pre_dea) and (stock_indicator.dif <= stock_indicator.dea):
            indicator="pre_dif:{},pre_dea:{},dif:{},dea:{}".format(stock_indicator.pre_dif,
                                                                        stock_indicator.pre_dea, stock_indicator.dif,
                                                                        stock_indicator.dea)
            ret = True
        return (ret,self.name,indicator)
