from abc import abstractmethod
from quant.signals.signalbase import SignalBase

# kdj
class KdjSignal(SignalBase):

    def __init__(self):
        self.name="KdjSignal"

    # 匹配买入信息
    # @classmethod
    def fit_buy(self, stock_indicator):
        ret = False
        indicator=''
        if (stock_indicator.k_pre < stock_indicator.d_pre) and (stock_indicator.k >= stock_indicator.d) :
            indicator="k_pre:{},d_pre:{},k:{},j:{}".format(stock_indicator.k_pre,
                                                                        stock_indicator.d_pre, stock_indicator.k,
                                                                        stock_indicator.d)
            ret=True
        return (ret,self.name,indicator)

    # 匹配卖出信息
    # @abstractmethod
    def fit_sell(self, stock_indicator):
        ret = False
        indicator = ''
        if(stock_indicator.k_pre > stock_indicator.d_pre) and (stock_indicator.k <= stock_indicator.d):
            indicator="k_pre:{},d_pre:{},j_pre:{},k:{},d:{},j:{}".format(stock_indicator.k_pre,
                                                                        stock_indicator.d_pre, stock_indicator.j_pre,stock_indicator.k,
                                                                        stock_indicator.d,stock_indicator.j)
            ret = True
        return (ret,self.name,indicator)
