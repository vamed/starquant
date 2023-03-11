# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:策略调用引擎
# Copyright (C) 2021-2023
###############################################################################
#
from __future__ import print_function, absolute_import
import sys,os
base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中
from quant.enums.strategytype import StrategyType

import importlib

# 策略引擎
class StrategyEngine():

    def __init__(self,context,strategy_list,broker,send_order_event_handler):
        # strategy_names= enumutil.getItems(Strategys)
        self.strategy_list =strategy_list
        self.context=context
        # strategy_names = ['MeanRevertingStrategy', 'RiskStrategy', 'TrendFollowingStrategy', 'DayTradingStrategy']
        # strategy_names = ['RiskStrategy']
        self.strategys=dict()
        for s in self.strategy_list:
            s=s.strip()
            if s!='':
                self.strategys[s]=self.init_strategy(s,context,broker,send_order_event_handler)


    def init_strategy(self,strategy_name,context,broker,send_order_event_handler):
        imp_class = getattr(importlib.import_module("quant.strategys.{}".format(strategy_name.lower())),
                            strategy_name)
        cls_obj = imp_class(context,broker,send_order_event_handler)
        return cls_obj

    def run(self,context,stock_indicator,bar=None,tick=None):
        if stock_indicator.strategy!="":
            # 运行股票选定策略
            if stock_indicator.strategy in self.strategys.keys():
                if bar and self.strategys[stock_indicator.strategy].drive_type == StrategyType.bar.value:
                    self.strategys[stock_indicator.strategy].run(context, bar, stock_indicator)
                elif tick and (self.strategys[stock_indicator.strategy].drive_type==StrategyType.tick.value):
                    self.strategys[stock_indicator.strategy].run(context, tick, stock_indicator)

            # 运行全域策略
            for key in self.strategys:
                if key!=stock_indicator.strategy:
                    if bar and (self.strategys[key].drive_type == StrategyType.bar.value):
                        self.strategys[key].run(context, bar, stock_indicator)
                    elif tick and (self.strategys[key].drive_type == StrategyType.tick.value):
                        self.strategys[key].run(context, tick, stock_indicator)
        else:
            for key in self.strategys:
                if bar and (self.strategys[key].drive_type==StrategyType.bar.value):
                    self.strategys[key].run(context,bar,stock_indicator)
                elif tick and (self.strategys[key].drive_type==StrategyType.tick.value):
                    self.strategys[key].run(context, tick, stock_indicator)

    # 运行定时策略
    def run_schedule(self):
        for key in self.strategys:
            if self.strategys[key].drive_type == StrategyType.schedule.value:
                self.strategys[key].run_schedule()

    def update_order_symbols(self):
        for key in self.strategys:
            self.strategys[key].update_order_symbols()

if __name__=="__main__":

    # df = StockPool().get_picktime()

    # stock_indicator = get_obj_from_df(df, StockIndicator)
    # StrategyEngine().run('','',stock_indicator)
    pass
