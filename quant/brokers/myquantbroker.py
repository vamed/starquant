# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:掘金经纪商封装
# Copyright (C) 2021-2023
###############################################################################
#
from gm.api import order_volume, get_unfinished_orders, order_cancel, order_close_all, order_cancel_all, \
    order_target_percent
from gm.enum import OrderSide_Sell, OrderType_Limit, PositionEffect_Open, PositionSide_Long, OrderSide_Buy, \
    PositionEffect_Close, MODE_LIVE, MODE_BACKTEST, OrderType_Market

from quant.brokers.broker import Broker
from quant.account import Account
from quant.enums.orderside import OrderSides
from quant.model.asset import Asset
from quant.model.order import Order
from quant.model.position import Position
import pandas as pd
from quant.util import stockutil

# 掘金经纪商
class MyquantBroker(Broker):
    #
    def __init__(self,context):
        self.trade_records = dict()
        self.context = context
        self.account = Account(self.context)

    #限价买入指定量的股票
    def buy(self,symbol,volume,price,factor,strategy,indicator=''):
        ret=order_volume(symbol=symbol, volume=volume, side=OrderSide_Buy, order_type=OrderType_Limit,
                         position_effect=PositionEffect_Open, price=price)
        print(ret)
        # 发送订单回回调
        self.send_order_callback(self.account.get_account_id(),ret[0].cl_ord_id,symbol,OrderSides.OrderSide_Buy.value, price, volume,factor,strategy,indicator,self.context.now)
        return ret

    # 限价买出指定量的股票
    def sell(self,symbol,volume,price,factor,strategy,indicator=''):
        ret=order_volume(symbol=symbol, volume=volume, side=OrderSide_Sell, order_type=OrderType_Limit,
                         position_effect=PositionEffect_Close, price=price)
        print(ret)
        # 发送订单回回调
        self.send_order_callback( self.account.get_account_id(),ret[0].cl_ord_id, symbol, OrderSides.OrderSide_Sell.value, price,
                                      volume,factor,strategy,indicator,self.context.now)

    # 清仓某股票仓位
    def sell_out(self,symbol,price,factor,strategy,indicator=''):
        pos=self.getSymbolPosition(symbol)
        if pos.account_id:
            if (pos.can_use_volume>0):
                volume=pos.can_use_volume
                self.sell(symbol,volume=volume,price=price,factor=factor,strategy=strategy,indicator=indicator)


    #限价买入指定量的股票
    def order_target_percent(self,symbol,percent,factor,strategy,indicator=''):
        ret=order_target_percent(symbol=symbol, percent=percent,
                             order_type=OrderType_Market,
                             position_side=PositionSide_Long)
        # 发送订单回回调
        if ret[0].side==1:
            side=OrderSides.OrderSide_Buy.value
        else:
            side = OrderSides.OrderSide_Sell.value
        self.send_order_callback(self.account.get_account_id(),ret[0].cl_ord_id,symbol,side, ret[0].price, ret[0].volume,factor,strategy,indicator,self.context.now)

        return ret
    # 清仓
    def close_all(self):
        # 先撤消所有委托
        order_cancel_all()
        # 清仓
        order_close_all()

    # 判断是否有未完成的订单
    def has_unfinished_orders(self,code,side):
        ret=False
        orders = get_unfinished_orders()
        for i,o in enumerate(orders):
            if (o.symbol==code) and (o.side==side):
                ret=True
                break
        return ret

    # 订单取消
    def cancel_order(self,code,side):
        orders = get_unfinished_orders()
        ords=[]
        if side==0:
            for i, o in enumerate(orders):
                order = {'cl_ord_id': o['cl_ord_id'], 'account_id': o['account_id']}
                ords.append(order)
        else:
            for i, o in enumerate(orders):
                if (code!='') and (o.symbol != code):
                    continue
                if (side!=0) and (o.side != side):
                    continue
                order = {'cl_ord_id': o['cl_ord_id'], 'account_id': o['account_id']}
                ords.append(order)

        order_cancel(wait_cancel_orders=ords)

    # 获取当前资产总金额
    def getCapital(self):
        account = self.context.account()
        capital=account.cash.nav
        return capital

    # 获取帐号资产信息
    def getAsset(self):
        asset=Asset()
        account = self.context.account()
        asset.account_id=account.cash.account_id
        asset.account_name = account.cash.account_name
        asset.total_asset=account.cash.nav
        asset.cash=account.cash.available
        asset.frozen_cash=account.cash.order_frozen
        asset.market_value=account.cash.market_value
        asset.fpnl=account.cash.fpnl
        asset.initial_capital = self.account.initial_capital
        return asset

    # 获取当前持仓明细
    def getPositions(self,display=False):
        positions=[]
        pos = self.context.account().positions()
        symbols=[]
        for i in range(len(pos)):
            position=Position()
            # position.account_id=pos[i].account_id
            position.account_id=self.account.get_account_id()
            position.code = pos[i].symbol
            position.symbol = pos[i].symbol
            position.volume = pos[i].volume
            position.amount = pos[i].vwap*pos[i].volume
            position.on_road_volume = pos[i].volume_today
            position.frozen_volume = pos[i].order_frozen
            position.open_price=pos[i].vwap
            position.market_value = pos[i].market_value
            position.can_use_volume= position.volume-position.on_road_volume-position.frozen_volume
            position.price =round(position.market_value / position.volume, 2)
            position.profit_amount=position.market_value-position.amount
            position.date=pos[i].updated_at
            position.update_time=pos[i].updated_at
            position.created_at=pos[i].created_at
            position.profit_rate=round(position.profit_amount/position.amount*100,2)
            positions.append(position)
            symbols.append(pos[i].symbol)

        if self.context.mode == MODE_BACKTEST:
            pos=self.get_backtest_position(account_id=self.context.backtest_account_id,date=self.context.now.strftime("%Y-%m-%d"))
            for p in pos:
                if p.symbol not in symbols:
                    positions.append(p)

        if display==True:
            self.display_account_position_info(positions)
        return positions

    # 获取某股票当前持仓金额
    def getSymbolPosition(self,symbol):
        ret=Position()
        ret.market_value=0
        ret.can_use_volume=0
        pos = self.context.account().position(symbol=symbol, side=PositionSide_Long)
        if pos!=None:
            ret.account_id=pos.account_id
            ret.code = pos.symbol
            ret.symbol = pos.symbol
            ret.volume = pos.volume
            ret.amount = pos.cost
            ret.on_road_volume = pos.volume_today
            ret.frozen_volume = pos.order_frozen
            ret.open_price=pos.vwap
            ret.market_value = pos.market_value
            ret.can_use_volume= ret.volume-ret.on_road_volume-ret.frozen_volume
            ret.price =round(ret.market_value / ret.volume, 2)
            ret.profit_amount=ret.market_value-ret.amount
            ret.date=pos.updated_at
            ret.update_time = pos.updated_at
            ret.profit_rate=round(ret.profit_amount/ret.amount*100,2)
        elif self.context.mode == MODE_BACKTEST:
            for p in self.context.positions:
                if p.symbol == symbol:
                    ret=p
                    break
        return ret

    # 获取当前股票持仓比例
    def getSymbolPositionRate(self, symbol):
        capital = self.getCapital()
        pos=self.getSymbolPosition(symbol)
        ret = pos.market_value / capital
        return ret

    # 获取当前持仓股票数量
    def getStockNumber(self):
        positions = self.context.account().positions()
        ret=len(positions)
        return ret

    # 获取当前持仓金额
    def getPositionAmount(self):
        ret = 0
        positions = self.context.account().positions()
        if len(positions)>0:
            df=pd.DataFrame(positions)
            ret = df['amount'].sum()
        return ret

    # 获取仓位比例
    def getPositionRate(self):
        capital=self.getCapital()
        amount=self.getPositionAmount()
        ret=round((amount/capital),2)
        return ret

    #检查是否还有可买仓位
    def hasPosition(self):
        ret=True
        if self.getPositionRate()>=self.account.MAX_POSITION:
            ret=False
        return ret

    #检查是否超过持仓股票数限制
    def isUnderMaxStockNumber(self):
        ret=True
        if self.getStockNumber()>=self.account.MAX_STOCK_NUMBER:
            ret=False
        return ret

    #检查某股票是否超过持仓股票数限制
    def isUnderMaxStockPosition(self,symbol):
        ret=True
        if self.getSymbolPositionRate(symbol)>=self.account.MAX_SINGLE_POSITION:
            ret=False
        return ret

    # 获取回测持仓
    def get_backtest_position(self,account_id,date):
        df=Order().get_unfinished_order(account_id=account_id,date=date)

        positions=[]
        for i,row in df.iterrows():
            pos=Position()
            pos.account_id = row['account_id']
            pos.symbol=row['symbol']
            pos.code =stockutil.delSymbolPrefix(row['symbol'])
            pos.open_price=row['price']
            pos.volume=row['volume']
            pos.amount = pos.open_price * pos.volume
            pos.can_use_volume = row['volume']
            pos.frozen_volume = 0
            pos.on_road_volume = 0
            pos.price=pos.open_price
            pos.market_value=pos.amount
            pos.profit=0
            pos.profit_rate=0
            pos.profit_amount=0
            positions.append(pos)
        return positions