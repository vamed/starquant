# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:经纪商基类
# Copyright (C) 2021-2023
###############################################################################
#
import datetime
from abc import abstractmethod
from gm.enum import MODE_BACKTEST
from quant.model.order import Order
from quant.model.position import Position
from quant.util import numberutil

# 经纪商基类
class Broker(object):
    def __init__(self,context):
        self.context=context

    #限价买入指定量的股票
    @abstractmethod
    def buy(self,symbol,volume,price,factor,strategy,indicator):
        raise NotImplementedError('Method is required!')

    # 限价买出指定量的股票
    # @abstractmethod
    def sell(self,symbol,volume,price,factor,strategy,indicator):
        raise NotImplementedError('Method is required!')

    # 清仓
    @abstractmethod
    def sell_out(self,symbol,price,factor,strategy,indicator):
        raise NotImplementedError('Method is required!')

    #检查是否还有可买仓位
    @abstractmethod
    def hasPosition(self):
        raise NotImplementedError('Method is required!')

    #检查是否超过持仓股票数限制
    @abstractmethod
    def isUnderMaxStockNumber(self):
        raise NotImplementedError('Method is required!')

    #检查某股票是否超过持仓股票数限制
    @abstractmethod
    def isUnderMaxStockPosition(self,symbol):
        raise NotImplementedError('Method is required!')

    # 判断是否有未完成的订单
    @abstractmethod
    def has_unfinished_orders(self,symbol):
        raise NotImplementedError('Method is required!')

    # 金额转为量，并取整
    def get_amount(self,value,price):
        volume = int(value / price)
        volume = numberutil.get_neat(volume)
        return volume

    # 发送订单回回调
    def send_order_callback(self, account_id,cl_ord_id, symbol,side, price, volume,factor,strategy,indicator,trade_date):

        if self.send_order_event_handler:
            order = Order()
            order.account_id=account_id
            order.cl_ord_id = cl_ord_id
            order.symbol =symbol
            if side==2:
                side=-1
            order.side = side
            order.price = price
            order.volume = volume
            order.amount=price*volume
            order.factor = factor
            order.indicator = indicator
            order.strategy = strategy
            order.trade_date = trade_date.strftime('%Y-%m-%d')
            order.trade_time = trade_date
            order.record_time = datetime.datetime.now()
            order.status=1
            order.mode=self.context.mode
            # 更新持仓股票可用数
            if self.context.mode==MODE_BACKTEST:
                if order.side == -1:
                    for i in range(len(self.context.positions)):
                        if self.context.positions[i].symbol == order.symbol:
                            self.context.positions[i].volume = self.context.positions[i].volume - order.volume
                            self.context.positions[i].can_use_volume = self.context.positions[i].can_use_volume - order.volume
                            if self.context.positions[i].volume<0:
                                self.context.positions[i].volume=0
                            if self.context.positions[i].can_use_volume<0:
                                self.context.positions[i].can_use_volume=0
                            break
            order.insert()
            self.send_order_event_handler(order)

    # 屏幕打印帐号持仓信息
    def display_account_position_info(self,pos):
        print("=========================当前帐号持仓信息===============================")
        if len(pos)>0:
            df=Position().to_df(pos)
            market_value=df['market_value'].sum()
            profit=df['profit_amount'].sum()
            print("当前持股数：{}".format(len(df)))
            print("当前持仓金额：{:.2f}元".format(market_value))
            print("当前持仓收益：{:.2f}元".format(profit))
            print("当前持仓收益率：{:.2f}%".format(profit/(market_value-profit)*100))
            print(df)
        else:
            print("当前帐号没有持仓")

    # 屏幕打印帐号资金信息
    def display_account_asset_info(self):
        asset=self.getAsset()
        print("=========================资金信息===============================")
        print("当前运行帐号：{},id:{}".format(asset.account_name,asset.account_id))
        print("初始总资金：{:.2f}元".format(asset.initial_capital))
        print("帐号总资产现值：{:.2f}元".format(asset.total_asset))
        print("总收益：{:.2f}元".format(asset.total_asset-asset.initial_capital))
        print("总收益率：{:.2f}%".format((asset.total_asset-asset.initial_capital)/asset.initial_capital*100))
        print("当前持仓市值：{:.2f}元".format(asset.market_value))
        print("当前持仓位：{:.2f}%".format(asset.market_value/asset.initial_capital*100))
        print("当前可用资金：{:.2f}元".format(asset.cash))