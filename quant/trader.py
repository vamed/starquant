# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function: 交易类
# Copyright (C) 2015-2020
###############################################################################

from gm.api import *
from quant.account import Account
from quant.logger import Logger
from quant.util import stockutil

# 交易类
class Trader():
    def __init__(self,context,broker):
        self.trade_records = dict()
        self.context=context
        self.account=Account(self.context)
        self.broker=broker

    def buy(self,symbol,price,value=None,factor='',strategy= 'strategy',indicator='',checkPos=True):
        ret=None
        if self.broker.hasPosition() == False:
            Logger().loginfo('已经超过设置最大仓位')
            return
        if (self.broker.isUnderMaxStockNumber() == False) and checkPos:
            Logger().loginfo('已经超过设置最大持仓股数据')
            return
        if (self.broker.isUnderMaxStockPosition(symbol) == False):
            Logger().loginfo('已经超过设置单股最大持仓金额')
            return
        if value==None:
            value=self.account.PER_BUY_AMOUNT
        if self.has_unfinished_orders(symbol)==False:
            self.trade_records[symbol] = factor
            volume=stockutil.value_to_volume(value,price)
            ret=self.broker.buy(symbol=symbol, volume=volume, price=price,factor=factor,indicator=indicator,strategy= strategy)
            Logger().loginfo('----------buy--------')
        return ret


    def order_target_percent(self,symbol,percent,factor='',strategy= 'strategy',indicator='',checkPos=True):
        ret = self.broker.order_target_percent(symbol=symbol, percent=percent, factor=factor, indicator=indicator,
                                               strategy=strategy)
        Logger().loginfo(ret)
        return ret
    # 清仓股票
    def sell_out(self,symbol,price,factor='',indicator='',strategy= 'strategy'):
        self.broker.sell_out(symbol,price,factor=factor,indicator=indicator,strategy= strategy)
        self.trade_records[symbol] =factor

    #卖出股票
    def sell(self,symbol,price,volume,factor='',indicator='',strategy= 'strategy'):
        self.broker.sell(symbol,volume,price,factor=factor,indicator=indicator,strategy= strategy)
        self.trade_records[symbol] =factor

    # 清仓所有仓位
    def close_all(self):
        self.broker.close_all()
    # 止损
    def stop_lost(self,symbol,cost,price):
        if cost*0.9>price:
            self.sell_target_volume(symbol, price, 0, "stop_lost")
            print("stop_lost")

    def has_unfinished_orders(self,code):
        ret=False
        orders = get_unfinished_orders()
        for i,o in enumerate(orders):
            if o.symbol==code:
                ret=True
                break
        return ret

    # 订单取消
    def cancel_order(self,code,side):
        self.broker.cancel_order(code,side)
