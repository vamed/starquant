# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:信号类
# Copyright (C) 2021-2023
###############################################################################
#

import importlib
from quant.util import stringutil

class SignalEngine():

    def __init__(self,signal_list):
        self.signal_list =signal_list
        self.signals=dict()
        for s in self.signal_list:
            s=s.strip()
            if s!='':
                self.signals[s]=self.init_signals(s)

    # 初始化信息对象
    def init_signals(self,signal_name):
        imp_class = getattr(importlib.import_module("quant.signals.{}".format(signal_name.lower())),
                            signal_name)
        cls_obj = imp_class()
        return cls_obj

    # @classmethod
    def fit_buy(self, stock_indicator):
        ret = False
        fit_name=[]
        fit_indicator=[]
        for sig_name in self.signals:
            ret_fit=self.signals[sig_name].fit_buy(stock_indicator)
            if ret_fit[0]:
                fit_name.append("{}_fit_buy".format(ret_fit[1]))
                fit_indicator.append(ret_fit[2])
                ret=True

        return (ret,stringutil.array_to_string(fit_name),stringutil.array_to_string(fit_indicator))

    # @classmethod
    def fit_sell(self, stock_indicator):
        ret = False
        fit_name = []
        fit_indicator = []
        for sig_name in self.signals:
            ret_fit=self.signals[sig_name].fit_sell(stock_indicator)
            if ret_fit[0]:
                fit_name.append("{}_fit_sell".format(ret_fit[1]))
                fit_indicator.append(ret_fit[2])
                ret=True
        return (ret,stringutil.array_to_string(fit_name),stringutil.array_to_string(fit_indicator))

if __name__=="__main__":
    pass
    # df = PickTime().getStock()
    # df.set_index('code',inplace=True)
    # if FactorEngine().fit(df.loc['600056'],10)==True:
    #     print('fddddddddddddddd')
    # else:
    #     print('111111111111111111')